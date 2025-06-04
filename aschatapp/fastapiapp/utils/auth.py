import jwt
from fastapi import HTTPException

from ..config import SECRET_KEY
from .logging_config import get_logger

logger = get_logger(__name__)


async def get_user_from_token(token: str) -> dict:
    """Decode JWT token locally and return user information."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    logger.info("Decoding token...")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id") or payload.get("id")
        if not user_id:
            raise credentials_exception
        username = payload.get("username")
        user_data = {"id": user_id, "username": username}
        logger.info(f"Token decoded, user_id: {user_id}")
        return user_data
    except jwt.PyJWTError as exc:
        logger.error(f"JWT decode failed: {exc}")
        raise credentials_exception
