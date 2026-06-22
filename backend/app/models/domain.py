import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from .base import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    github_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=True)
    name = Column(String)
    
    # Personal API Keys stored in DB per user
    github_access_token = Column(String, nullable=True)
    openai_api_key = Column(String, nullable=True)

class Repository(Base):
    __tablename__ = "repositories"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    github_repo_id = Column(String, unique=True, index=True)
    name = Column(String)
    url = Column(String)
    is_active = Column(Boolean, default=True)

class PullRequest(Base):
    __tablename__ = "pull_requests"
    id = Column(String, primary_key=True, default=generate_uuid)
    repo_id = Column(String, ForeignKey("repositories.id"))
    pr_number = Column(String)
    title = Column(String)
    status = Column(String)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(String, primary_key=True, default=generate_uuid)
    pr_id = Column(String, ForeignKey("pull_requests.id"))
    commit_sha = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    quality_score = Column(Float, default=0.0)
    security_score = Column(Float, default=0.0)

class Finding(Base):
    __tablename__ = "findings"
    id = Column(String, primary_key=True, default=generate_uuid)
    review_id = Column(String, ForeignKey("reviews.id"))
    file_path = Column(String)
    line_number = Column(Integer)
    type = Column(String)  # security, bug, smell
    severity = Column(String)
    description = Column(String)
    suggested_fix = Column(String)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    repo_id = Column(String, ForeignKey("repositories.id"))
    created_at = Column(DateTime, server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String) # 'user' or 'ai'
    content = Column(String)
    created_at = Column(DateTime, server_default=func.now())
