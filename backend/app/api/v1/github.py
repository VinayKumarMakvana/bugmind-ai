from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
import os

from ...db.session import get_db
from ...models.domain import User, Repository
from ...core.security import decode_access_token

router = APIRouter()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://bugmind-ai.vercel.app")

@router.get("/login")
def github_login(token: str = Query(...)):
    # Redirect to GitHub OAuth
    # We pass the JWT token in the 'state' parameter so we know who the user is on the callback
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&state={token}&scope=repo"
    return RedirectResponse(url=github_auth_url)

@router.get("/callback")
async def github_callback(code: str, state: str, db: Session = Depends(get_db)):
    if not GITHUB_CLIENT_SECRET:
        # Fallback to just returning to dashboard if secret is not configured
        return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?error=missing_github_secret")
        
    # Decode the JWT token from the state parameter
    payload = decode_access_token(state)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid state token")
        
    user_email = payload["sub"]
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code
            }
        )
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?error=github_oauth_failed")
            
        # Save token
        user.github_access_token = access_token
        db.commit()
        
        # Fetch user's repositories
        repos_response = await client.get(
            "https://api.github.com/user/repos?sort=updated&per_page=10",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github.v3+json"}
        )
        
        if repos_response.status_code == 200:
            repos_list = repos_response.json()
            for repo_data in repos_list:
                # Check if repo already exists
                existing = db.query(Repository).filter(Repository.github_repo_id == str(repo_data["id"])).first()
                if not existing:
                    new_repo = Repository(
                        name=repo_data["full_name"],
                        github_repo_id=str(repo_data["id"]),
                        url=repo_data["html_url"],
                        user_id=user.id
                    )
                    db.add(new_repo)
            db.commit()

    # Redirect back to frontend dashboard
    return RedirectResponse(url=f"{FRONTEND_URL}/dashboard")
