import uuid
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def generate_uuid():
    return str(uuid.uuid4())

class User(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    email: str
    password_hash: Optional[str] = None
    name: Optional[str] = None
    openai_api_key: Optional[str] = None

class Repository(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    user_id: str
    name: str
    url: Optional[str] = None
    github_repo_id: Optional[str] = None
    local_path: Optional[str] = None
    is_active: bool = True
    latest_score: float = 100.0
    issues_count: int = 0
    prs_count: int = 0

class PullRequest(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    repo_id: str
    pr_number: str
    title: str
    status: str

class Review(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    pr_id: str
    commit_sha: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quality_score: float = 0.0
    security_score: float = 0.0

class Finding(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    review_id: str
    file_path: str
    line_number: int
    type: str
    severity: str
    description: str
    suggested_fix: str

class ChatSession(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    user_id: str
    repo_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    session_id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
