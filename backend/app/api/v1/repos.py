from __future__ import annotations

import logging
import os
import shutil
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile

from ...api.deps import get_current_user
from ...db.session import get_db
from ...models.domain import Repository, User
from ...tasks.worker import process_local_review

logger = logging.getLogger(__name__)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# CONSTANTS
# =========================================================

ALLOWED_EXTENSIONS = {
    ".htm", ".html", ".js", ".jsx", ".ts", ".tsx", ".css", ".json",
    ".py", ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".php", ".rb",
    ".swift", ".kt", ".dart", ".sql", ".yaml", ".md", ".sh"
}


# =========================================================
# UPLOAD REPOSITORY
# =========================================================

@router.post("/upload")
async def upload_repository(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    repo_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Any = Depends(get_db),
) -> Dict[str, str]:
    """
    Upload a standalone repository/files and trigger local static analysis.
    """

    repo_id = str(uuid.uuid4())
    workspace_dir = os.path.join(os.getcwd(), "workspaces", repo_id)
    os.makedirs(workspace_dir, exist_ok=True)

    logger.info(
        "Started uploading repository '%s' to workspace '%s'",
        repo_name,
        workspace_dir,
    )

    for file in files:
        if not file.filename:
            continue
            
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            logger.debug("Skipping file with unsupported extension: %s", file.filename)
            continue

        # Use base name to avoid malicious paths
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(workspace_dir, safe_filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    new_repo = Repository(
        id=repo_id,
        user_id=current_user.id,
        name=repo_name,
        local_path=workspace_dir,
    )
    
    await db.repositories.insert_one(
        new_repo.model_dump()
    )

    # Trigger local review process
    if background_tasks:
        background_tasks.add_task(
            process_local_review,
            repo_id=repo_id,
            local_path=workspace_dir,
            user_openai_api_key=current_user.openai_api_key,
        )
    else:
        process_local_review(
            repo_id=repo_id,
            local_path=workspace_dir,
            user_openai_api_key=current_user.openai_api_key,
        )

    logger.info(
        "Successfully saved repository '%s' (ID: %s) for local review.",
        repo_name,
        repo_id,
    )

    return {
        "status": "success",
        "repo_id": repo_id,
    }


# =========================================================
# DASHBOARD
# =========================================================

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Any = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Fetch the list of repositories and scores for the current user's dashboard.
    """

    repos_cursor = db.repositories.find(
        {
            "user_id": current_user.id
        }
    )
    
    repos = await repos_cursor.to_list(length=100)
    dashboard_data = []

    for repo in repos:
        dashboard_data.append({
            "id": repo["id"],
            "name": repo["name"],
            "prs": repo.get("prs_count", 0),
            "issues": repo.get("issues_count", 0),
            "score": round(repo.get("latest_score", 100.0)),
        })

    return dashboard_data

