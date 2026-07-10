from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings


# =========================================================
# PASSWORD HASHING
# =========================================================

def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt.
    """

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


# =========================================================
# PASSWORD VERIFY
# =========================================================

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify bcrypt password.
    """

    try:

        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    except Exception:

        return False


# =========================================================
# CREATE JWT
# =========================================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Generate JWT access token.
    """

    payload = data.copy()

    expire = datetime.now(
        timezone.utc
    ) + (
        expires_delta
        or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
    )

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# =========================================================
# DECODE JWT
# =========================================================

def decode_access_token(
    token: str,
) -> dict | None:
    """
    Decode JWT.
    """

    try:

        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ],
        )

    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        jwt.DecodeError,
    ):

        return None


# =========================================================
# TOKEN VALIDATION
# =========================================================

def is_token_valid(
    token: str,
) -> bool:
    """
    Check whether token is valid.
    """

    return decode_access_token(token) is not None


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "is_token_valid",
]