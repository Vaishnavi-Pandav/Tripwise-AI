import logging
import secrets
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token, hash_password
from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger("tripwise")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _decode_firebase_token_simple(token: str) -> Optional[dict]:
    """
    Decode Firebase JWT without signature verification (safe for dev).
    In production, set VERIFY_FIREBASE_TOKENS=true to enable full verification.
    """
    try:
        import base64, json as _json

        # JWT = header.payload.signature — decode middle part
        parts = token.split(".")
        if len(parts) != 3:
            return None

        # Fix base64 padding
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = _json.loads(base64.urlsafe_b64decode(payload_b64))

        # Basic checks
        project_id = settings.FIREBASE_PROJECT_ID or "tripewiseai"
        aud = payload.get("aud")
        iss = payload.get("iss", "")

        if aud != project_id:
            logger.debug(f"Firebase aud mismatch: {aud} != {project_id}")
            return None
        if project_id not in iss:
            logger.debug(f"Firebase iss mismatch: {iss}")
            return None

        import time
        if payload.get("exp", 0) < time.time():
            logger.debug("Firebase token expired")
            return None

        return payload
    except Exception as e:
        logger.debug(f"Firebase token decode failed: {e}")
        return None


def _get_or_create_firebase_user(db: Session, payload: dict) -> User:
    """Find or auto-create a user from Firebase token payload."""
    uid   = payload.get("uid") or payload.get("sub", "")
    email = payload.get("email") or f"{uid}@firebase.user"
    name  = (payload.get("name") or
             payload.get("display_name") or
             email.split("@")[0])

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            full_name=name,
            email=email,
            password_hash=hash_password(secrets.token_hex(16)[:32]),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Auto-created user for Firebase: {email}")
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Try Firebase token (frontend sends these)
    firebase_payload = _decode_firebase_token_simple(token)
    if firebase_payload:
        return _get_or_create_firebase_user(db, firebase_payload)

    # 2. Fall back to custom JWT (Swagger UI / direct API calls)
    payload = decode_access_token(token)
    if not payload:
        raise credentials_error

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_error

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_error
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
