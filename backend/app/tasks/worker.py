import time
import os
import json
from ..services.static_analysis import aggregate_findings
from ..services.scoring import calculate_scores
from ..services.ast_parser import chunk_repository
from ..services.rag import store_chunks, retrieve_context
from ..services.ai_reviewer import generate_review
from ..db.session import db
from ..models.domain import Repository, Review, Finding
import asyncio
from ..core.config import settings
from ..core.events import event_manager

def publish_event(event_type: str, data: dict):
    try:
        event_manager.publish_sync(event_type, data)
    except Exception as e:
        print(f"Failed to publish event: {e}")

def process_local_review(repo_id: str, local_path: str):
    """
    Analyzes the uploaded repository directly from the local file system.
    Runs in a background thread via FastAPI BackgroundTasks.
    """
    print(f"Starting review for local Repo {repo_id} at {local_path}")
    publish_event("review_started", {"repo_id": repo_id, "status": "Initializing local analysis..."})
    
    publish_event("review_progress", {"repo_id": repo_id, "status": "Parsing AST and generating embeddings..."})
    
    # Extract Context and Update RAG Store
    chunks = chunk_repository(local_path)
    store_chunks(repo_id, chunks)
    
    publish_event("review_progress", {"repo_id": repo_id, "status": "Running static analysis engines..."})
    
    # Run Unified Findings Engine
    findings = aggregate_findings(local_path)
    
    publish_event("review_progress", {"repo_id": repo_id, "status": "Consulting AI Copilot..."})
    
    # Contextual AI Review Pipeline
    query = findings[0]["description"] if findings else "security vulnerabilities and best practices"
    context = retrieve_context(repo_id, query)
    context_text = [context] if context else []
    
    enriched_findings = generate_review("Local workspace review", findings, context_text)
    
    # Calculate Scores (Using enriched findings)
    quality_score, security_score = calculate_scores(enriched_findings)
    
    # Save to Database
    async def save_to_db():
        repo = await db.repositories.find_one({"id": repo_id})
        if not repo:
            print(f"Repo {repo_id} not found in DB")
            return
            
        new_review = Review(pr_id="local", commit_sha="local", quality_score=quality_score, security_score=security_score)
        review_dict = new_review.model_dump()
        review_dict["repo_id"] = repo_id # Add it since dashboard expects it
        await db.reviews.insert_one(review_dict)
        
        for finding_data in enriched_findings:
            new_finding = Finding(
                review_id=review_dict["id"],
                file_path=finding_data.get("file_path", ""),
                line_number=finding_data.get("line_number", 0),
                type="security" if "security" in str(finding_data.get("description", "")).lower() else "smell",
                severity=finding_data.get("severity", "low"),
                description=finding_data.get("description", ""),
                suggested_fix=finding_data.get("suggested_fix", "Review and update.")
            )
            await db.findings.insert_one(new_finding.model_dump())
            
        # Cache score and issue count on Repository document to fix N+1 query problem
        await db.repositories.update_one(
            {"id": repo_id},
            {"$set": {
                "latest_score": quality_score,
                "issues_count": len(enriched_findings)
            }}
        )
            
    # We must run this async function since process_local_review is synchronous
    # but asyncio.run might fail if we are already in an event loop.
    # Since it's run via BackgroundTasks (in a threadpool), asyncio.run is safe.
    try:
        asyncio.run(save_to_db())
    except RuntimeError:
        # If somehow there's an existing loop in this thread
        loop = asyncio.get_event_loop()
        loop.run_until_complete(save_to_db())
    
    publish_event("review_completed", {"repo_id": repo_id, "findings_count": len(enriched_findings)})
    print(f"Completed local review for {repo_id}.")
    return {"status": "success", "repo_id": repo_id, "findings_count": len(enriched_findings)}
