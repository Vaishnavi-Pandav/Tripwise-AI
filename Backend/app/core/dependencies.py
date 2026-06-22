import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

logger = logging.getLogger("tripwise")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _verify_firebase_token(token: str) -> dict | None:
    """Try to verify a Firebase ID token. Returns decoded payload or None."""
    try:
        import firebase_admin
        from firebase_admin import auth as firebase_auth
        # Initialise app if not already done
        if not firebase_admin._apps:
            from app.core.firebase_admin_setup import init_firebase
            init_firebase()
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except Exception as e:
        logger.debug(f"Firebase token verification failed: {e}")
        return None


def _get_or_create_firebase_user(db: Session, firebase_payload: dict) -> User:
    """
    Find user by Firebase UID stored in email field, or create a stub user.
    Firebase UID is used as a stable identifier.
    """
    uid   = firebase_payload.get("uid", "")
    email = firebase_payload.get("email", f"{uid}@firebase.user")
    name  = firebase_payload.get("name") or firebase_payload.get("email", "User").split("@")[0]

    # Look up by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Auto-create user on first login via Firebase
        from app.core.security import hash_password
        import secrets
        user = User(
            full_name=name,
            email=email,
            password_hash=hash_password(secrets.token_hex(16)),  # random unusable password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Auto-created user for Firebase UID: {uid}")
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

    # 1. Try Firebase token first (frontend sends these)
    firebase_payload = _verify_firebase_token(token)
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
