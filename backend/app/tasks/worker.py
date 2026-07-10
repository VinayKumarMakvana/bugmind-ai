from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from ..core.events import event_manager
from ..db.session import db
from ..models.domain import Finding, Repository, Review
from ..services.ai_reviewer import generate_review
from ..services.ast_parser import chunk_repository
from ..services.rag import retrieve_context, store_chunks
from ..services.scoring import calculate_scores
from ..services.static_analysis import aggregate_findings

logger = logging.getLogger(__name__)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def publish_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Safely publish an event to the global event manager.
    """
    try:
        event_manager.publish_sync(event_type, data)
    except Exception as e:
        logger.error("Failed to publish event: %s", e)


# =========================================================
# BACKGROUND TASKS
# =========================================================

def process_local_review(
    repo_id: str,
    local_path: str,
    user_openai_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyzes the uploaded repository directly from the local file system.
    Runs in a background thread via FastAPI BackgroundTasks.
    """

    logger.info("Starting review for local Repo %s at %s", repo_id, local_path)

    publish_event(
        "review_started",
        {"repo_id": repo_id, "status": "Initializing local analysis..."}
    )
    
    # ==========================================
    # 1. Parsing AST and Generating Embeddings
    # ==========================================
    publish_event(
        "review_progress",
        {"repo_id": repo_id, "status": "Parsing AST and generating embeddings..."}
    )
    
    chunks = chunk_repository(local_path)
    store_chunks(repo_id, chunks)
    
    # ==========================================
    # 2. Running Static Analysis Engines
    # ==========================================
    publish_event(
        "review_progress",
        {"repo_id": repo_id, "status": "Running static analysis engines..."}
    )
    
    findings = aggregate_findings(local_path)

    # Convert to expected format for AI reviewer
    formatted_findings = []
    for idx, f in enumerate(findings):
        formatted_findings.append({
            "id": str(idx),
            "file": f.get("file", ""),
            "line": f.get("line", 0),
            "description": f.get("message", ""),
            "severity": f.get("severity", "LOW"),
        })
    
    # ==========================================
    # 3. Consulting AI Copilot
    # ==========================================
    publish_event(
        "review_progress",
        {"repo_id": repo_id, "status": "Consulting AI Copilot..."}
    )
    
    query = formatted_findings[0]["description"] if formatted_findings else "security vulnerabilities and best practices"
    context = retrieve_context(repo_id, query)
    context_text = [context] if context else []
    
    review = generate_review(
        pr_diff="Local workspace review",
        findings=formatted_findings,
        context_chunks=context_text,
        user_openai_api_key=user_openai_api_key,
    )

    enriched_findings = review.get("findings", [])
    
    # ==========================================
    # 4. Calculate Scores
    # ==========================================
    quality_score, security_score = calculate_scores(enriched_findings)
    
    # ==========================================
    # 5. Save to Database (Async Context)
    # ==========================================
    async def save_to_db() -> None:
        repo = await db.repositories.find_one({"id": repo_id})
        
        if not repo:
            logger.error("Repo %s not found in DB", repo_id)
            return
            
        new_review = Review(
            pr_id="local",
            commit_sha="local",
            quality_score=quality_score,
            security_score=security_score,
        )
        
        review_dict = new_review.model_dump()
        review_dict["repo_id"] = repo_id
        
        await db.reviews.insert_one(review_dict)
        
        for issue in enriched_findings:
            title = issue.get("title", "")
            description = (
                f"**Why:** {issue.get('why', '')}\n\n"
                f"**Fix:** {issue.get('fix', '')}\n\n"
                f"**Example:**\n```\n{issue.get('example', '')}\n```"
            )

            new_finding = Finding(
                review_id=review_dict["id"],
                file_path=issue.get("file", ""),
                line_number=issue.get("line", 0),
                type="security" if "security" in title.lower() else "smell",
                severity=issue.get("severity", "LOW"),
                description=title,
                suggested_fix=description,
            )

            await db.findings.insert_one(new_finding.model_dump())
            
        # Cache score and issue count on Repository document to fix N+1 query problem
        await db.repositories.update_one(
            {"id": repo_id},
            {"$set": {
                "latest_score": quality_score,
                "issues_count": len(enriched_findings),
            }}
        )
            
    # Execute async db save safely in thread
    try:
        asyncio.run(save_to_db())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(save_to_db())
    
    publish_event(
        "review_completed",
        {"repo_id": repo_id, "findings_count": len(enriched_findings)}
    )

    logger.info("Completed local review for %s.", repo_id)

    return {
        "status": "success",
        "repo_id": repo_id,
        "findings_count": len(enriched_findings),
    }

