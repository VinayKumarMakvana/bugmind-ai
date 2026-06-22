from fastapi import APIRouter, Request
from ...tasks.worker import process_pr_review

router = APIRouter()

@router.post("/github")
async def github_webhook(request: Request):
    payload = await request.json()
    
    # Check if it's a pull request event
    if "pull_request" in payload:
        pr_number = payload["pull_request"]["number"]
        repo_id = payload["repository"]["id"]
        
        # Dispatch Celery task
        process_pr_review.delay(repo_id, pr_number)
        
        return {"status": "accepted", "message": "PR review task enqueued"}
        
    return {"status": "ignored"}
