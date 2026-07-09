from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
import os
import shutil
import uuid
from typing import List
from ...db.session import get_db
from ...models.domain import User, Repository
from ...api.deps import get_current_user
from ...tasks.worker import process_local_review

router = APIRouter()

@router.post("/upload")
async def upload_repository(
    files: List[UploadFile] = File(...),
    repo_name: str = Form(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    repo_id = str(uuid.uuid4())
    workspace_dir = os.path.join(os.getcwd(), "workspaces", repo_id)
    os.makedirs(workspace_dir, exist_ok=True)
    allowed_extensions = {".htm", ".html", ".js", ".jsx", ".ts", ".tsx", ".css", ".json"}
    
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            continue
            
        file_path = os.path.join(workspace_dir, os.path.basename(file.filename))
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    new_repo = Repository(
        id=repo_id,
        user_id=current_user.id,
        name=repo_name,
        local_path=workspace_dir
    )
    await db.repositories.insert_one(new_repo.model_dump())
    
    # Trigger local review process
    if background_tasks:
        background_tasks.add_task(process_local_review, repo_id, workspace_dir)
    else:
        process_local_review(repo_id, workspace_dir)
    
    return {"status": "success", "repo_id": repo_id}

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    repos_cursor = db.repositories.find({"user_id": current_user.id})
    repos = await repos_cursor.to_list(length=100)
    
    dashboard_data = []
    for repo in repos:
        dashboard_data.append({
            "id": repo["id"],
            "name": repo["name"],
            "prs": repo.get("prs_count", 0),
            "issues": repo.get("issues_count", 0),
            "score": round(repo.get("latest_score", 100.0))
        })
        
    return dashboard_data
