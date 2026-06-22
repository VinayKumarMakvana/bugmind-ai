from .celery_app import celery_app
import time
import os
import shutil
import tempfile
import json
import redis
from ..services.static_analysis import aggregate_findings
from ..services.scoring import calculate_scores
from ..services.ast_parser import chunk_repository
from ..services.rag import store_chunks, retrieve_context
from ..services.ai_reviewer import generate_review
from ..db.session import SessionLocal
from ..models.domain import Repository, PullRequest, Review, Finding
from ..core.config import settings

# Setup Sync Redis client for publishing events
redis_client = redis.from_url(settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "redis://localhost:6379/0", decode_responses=True)

def publish_event(event_type: str, data: dict):
    try:
        redis_client.publish("bugmind_events", json.dumps({"type": event_type, "data": data}))
    except Exception as e:
        print(f"Failed to publish event: {e}")

@celery_app.task(name="process_pr_review")
def process_pr_review(repo_id: str, pr_number: str):
    """
    Simulates fetching a PR diff, running Unified Findings, publishing SSE events, and creating Agentic Auto-Fixes.
    """
    print(f"Starting review for Repo {repo_id}, PR {pr_number}")
    publish_event("review_started", {"repo_id": repo_id, "pr_number": pr_number, "status": "Cloning repository..."})
    
    # 1. Simulate Repository Checkout
    time.sleep(1) # Simulate network delay
    temp_dir = tempfile.mkdtemp(prefix=f"bugmind_repo_{repo_id}_")
    dummy_file_path = os.path.join(temp_dir, "app.py")
    
    with open(dummy_file_path, "w") as f:
        f.write("import sqlite3\n")
        f.write("def get_user(user_id):\n")
        f.write("    conn = sqlite3.connect('test.db')\n")
        f.write("    # VULNERABLE SQL INJECTION\n")
        f.write("    cursor = conn.execute(f'SELECT * FROM users WHERE id = {user_id}')\n")
        f.write("    return cursor.fetchone()\n")
        
    publish_event("review_progress", {"repo_id": repo_id, "pr_number": pr_number, "status": "Parsing AST and generating embeddings..."})
    
    # 2. Extract Context and Update RAG Store
    chunks = chunk_repository(temp_dir)
    store_chunks(repo_id, chunks)
    
    publish_event("review_progress", {"repo_id": repo_id, "pr_number": pr_number, "status": "Running static analysis engines..."})
    
    # 3. Run Unified Findings Engine
    findings = aggregate_findings(temp_dir)
    
    publish_event("review_progress", {"repo_id": repo_id, "pr_number": pr_number, "status": "Consulting AI Copilot..."})
    
    # 4. Contextual AI Review Pipeline
    query = findings[0]["description"] if findings else "security vulnerabilities and best practices"
    context = retrieve_context(repo_id, query)
    context_text = [context] if context else []
    
    enriched_findings = generate_review("Diff missing for mock", findings, context_text)
    
    # 5. Calculate Scores (Using enriched findings)
    quality_score, security_score = calculate_scores(enriched_findings)
    
    # 6. Save to Database
    db = SessionLocal()
    try:
        repo = db.query(Repository).filter(Repository.github_repo_id == repo_id).first()
        if not repo:
            repo = Repository(github_repo_id=repo_id, name=f"repo-{repo_id}")
            db.add(repo)
            db.commit()
            db.refresh(repo)
            
        pr = db.query(PullRequest).filter(PullRequest.repo_id == repo.id, PullRequest.pr_number == pr_number).first()
        if not pr:
            pr = PullRequest(repo_id=repo.id, pr_number=pr_number, title=f"PR #{pr_number}")
            db.add(pr)
            db.commit()
            db.refresh(pr)
            
        review = Review(pr_id=pr.id, commit_sha="mock_sha", quality_score=quality_score, security_score=security_score)
        db.add(review)
        db.commit()
        db.refresh(review)
        
        for finding_data in enriched_findings:
            finding = Finding(
                review_id=review.id,
                file_path=finding_data.get("file_path"),
                line_number=finding_data.get("line_number"),
                type="security" if "security" in str(finding_data.get("description", "")).lower() else "smell",
                severity=finding_data.get("severity"),
                description=finding_data.get("description"),
                suggested_fix=finding_data.get("suggested_fix", "Review and update.")
            )
            db.add(finding)
        db.commit()
    finally:
        db.close()
    
    # --- PHASE 5: AGENTIC AUTO-FIX SIMULATION ---
    if len(enriched_findings) > 0:
        publish_event("agent_action", {"repo_id": repo_id, "pr_number": pr_number, "status": "Agent generating Auto-Fix Branch..."})
        time.sleep(2) # Simulate agent reasoning and git operations
        
        # Real GitHub API Integration using User's personal token from DB
        db = SessionLocal()
        try:
            repo_record = db.query(Repository).filter(Repository.github_repo_id == repo_id).first()
            if repo_record and repo_record.user_id:
                from ..models.domain import User
                user_record = db.query(User).filter(User.id == repo_record.user_id).first()
                github_token = user_record.github_access_token if user_record else None
                
                # In a fully productionized version, this uses the user's token:
                # if github_token:
                #     requests.post(f"{settings.GITHUB_API_BASE_URL}/repos/{repo_id}/pulls", headers={"Authorization": f"Bearer {github_token}"}, ...)
        finally:
            db.close()
            
        # Simulated response URL (you can replace this with actual API response URL later)
        auto_fix_pr_url = f"https://github.com/{repo_id}/pull/auto-fix-1"
        publish_event("agent_action_complete", {
            "repo_id": repo_id, 
            "pr_number": pr_number, 
            "message": f"Agent autonomously created fix PR: {auto_fix_pr_url}"
        })

    # 7. Clean up
    shutil.rmtree(temp_dir)
    
    publish_event("review_completed", {"repo_id": repo_id, "pr_number": pr_number, "findings_count": len(enriched_findings)})
    print(f"Completed review for PR {pr_number}.")
    return {"status": "success", "repo_id": repo_id, "pr_number": pr_number, "findings_count": len(enriched_findings)}
