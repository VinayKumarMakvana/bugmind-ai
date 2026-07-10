from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.domain import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
) -> User:
    """
    Returns the authenticated user.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token.",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    payload = decode_access_token(token)

    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")

    if not user_id:
        raise credentials_exception

    user_data = await db.users.find_one(
        {
            "id": user_id
        }
    )

    if user_data is None:
        raise credentials_exception

    return User(**user_data)


async def get_optional_user(
    token: str | None = Depends(oauth2_scheme),
    db=Depends(get_db),
) -> User | None:
    """
    Returns authenticated user if token exists,
    otherwise None.
    """

    if not token:
        return None

    payload = decode_access_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")

    if not user_id:
        return None

    user_data = await db.users.find_one(
        {
            "id": user_id
        }
    )

    if user_data is None:
        return None

    return User(**user_data)


__all__ = [
    "get_current_user",
    "get_optional_user",
]