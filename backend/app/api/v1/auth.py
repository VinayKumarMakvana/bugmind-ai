from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from ...api.deps import get_current_user
from ...core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from ...db.session import get_db
from ...models.domain import User

logger = logging.getLogger(__name__)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    has_openai_key: bool


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    openai_api_key: Optional[str] = None


# =========================================================
# USER REGISTRATION
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in: UserCreate,
    db: Any = Depends(get_db),
) -> UserResponse:
    """
    Register a new user.
    """

    user_dict = await db.users.find_one(
        {
            "email": user_in.email
        }
    )

    if user_dict:

        logger.warning(
            "Registration failed. Email already exists: %s",
            user_in.email,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=get_password_hash(user_in.password),
    )

    await db.users.insert_one(
        new_user.model_dump()
    )

    logger.info(
        "User registered successfully: %s",
        new_user.email,
    )

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name or "",
        has_openai_key=bool(new_user.openai_api_key),
    )


# =========================================================
# USER LOGIN
# =========================================================

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Any = Depends(get_db),
) -> Dict[str, str]:
    """
    Authenticate user and return JWT token.
    """

    user_dict = await db.users.find_one(
        {
            "email": form_data.username
        }
    )

    if not user_dict or not user_dict.get("password_hash"):

        logger.warning(
            "Login failed for email: %s",
            form_data.username,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user_dict["password_hash"]):

        logger.warning(
            "Invalid password for email: %s",
            form_data.username,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user_dict["id"]}
    )

    logger.info(
        "User logged in successfully: %s",
        form_data.username,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# =========================================================
# GET CURRENT USER
# =========================================================

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get current authenticated user profile.
    """

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name or "",
        has_openai_key=bool(current_user.openai_api_key),
    )


# =========================================================
# UPDATE CURRENT USER
# =========================================================

@router.put("/me", response_model=UserResponse)
async def update_me(
    profile_in: UserProfileUpdate,
    db: Any = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Update current authenticated user profile.
    """

    update_data: Dict[str, Any] = {}

    if profile_in.name is not None:
        update_data["name"] = profile_in.name
        current_user.name = profile_in.name

    if profile_in.openai_api_key is not None:
        update_data["openai_api_key"] = profile_in.openai_api_key
        current_user.openai_api_key = profile_in.openai_api_key

    if update_data:
        await db.users.update_one(
            {
                "id": current_user.id
            },
            {
                "$set": update_data
            }
        )

        logger.info(
            "User profile updated: %s",
            current_user.email,
        )

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name or "",
        has_openai_key=bool(current_user.openai_api_key),
    )

