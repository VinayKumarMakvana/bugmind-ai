from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.domain import Repository, PullRequest, Review, Finding, User
from ...api.deps import get_current_user

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repos = db.query(Repository).filter(Repository.user_id == current_user.id).all()
    
    # Mock code removed to allow real Github repos to show up
    
    dashboard_data = []
    for repo in repos:
        prs = db.query(PullRequest).filter(PullRequest.repo_id == repo.id).count()
        
        latest_review = db.query(Review).join(PullRequest).filter(PullRequest.repo_id == repo.id).order_by(Review.created_at.desc()).first()
        score = latest_review.quality_score if latest_review else 100.0
        
        issues = 0
        if latest_review:
            issues = db.query(Finding).filter(Finding.review_id == latest_review.id).count()
            
        dashboard_data.append({
            "id": repo.id,
            "name": repo.name,
            "prs": prs,
            "issues": issues,
            "score": round(score)
        })
        
    return dashboard_data
