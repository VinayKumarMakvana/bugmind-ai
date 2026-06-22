from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
import os

from ...db.session import get_db
from ...models.domain import User, Repository
from ...core.security import decode_access_token, create_access_token

router = APIRouter()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://bugmind-ai.vercel.app")

@router.get("/login")
def github_login(token: str = Query(None)):
    # Redirect to GitHub OAuth
    state = token if token else "no_token"
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&state={state}&scope=repo%20user:email"
    return RedirectResponse(url=github_auth_url)

@router.get("/callback")
async def github_callback(code: str, state: str, db: Session = Depends(get_db)):
    if not GITHUB_CLIENT_SECRET:
        # Fallback to just returning to dashboard if secret is not configured
        return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?error=missing_github_secret")
        
    # Decode the JWT token if one was provided
    user = None
    if state and state != "no_token":
        payload = decode_access_token(state)
        if payload and "sub" in payload:
            user_email = payload["sub"]
            user = db.query(User).filter(User.email == user_email).first()

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
            
        # Get user profile to handle signup/login
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github.v3+json"}
        )
        if user_response.status_code != 200:
            return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?error=github_user_failed")
            
        github_user = user_response.json()
        github_id = str(github_user["id"])
        
        if not user:
            # Try to find by github_id
            user = db.query(User).filter(User.github_id == github_id).first()
            if not user:
                email = github_user.get("email")
                if not email:
                    emails_response = await client.get("https://api.github.com/user/emails", headers={"Authorization": f"Bearer {access_token}"})
                    emails = emails_response.json()
                    primary = next((e for e in emails if e.get("primary")), None)
                    email = primary["email"] if primary else (emails[0]["email"] if emails else f"{github_user['login']}@github.com")
                
                # Check if email exists
                user = db.query(User).filter(User.email == email).first()
                if not user:
                    user = User(email=email, name=github_user.get("name") or github_user.get("login"), github_id=github_id)
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                else:
                    user.github_id = github_id
        else:
            user.github_id = github_id

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

    # Generate JWT for frontend session
    jwt_token = create_access_token(data={"sub": user.email})

    # Redirect back to frontend dashboard with token
    return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?token={jwt_token}")
