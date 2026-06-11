from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserOut, UserUpdate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             summary="Register a new user")
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    return AuthService.signup(db, payload)


@router.post("/login", response_model=Token, summary="Login and get JWT token")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login(db, payload.email, payload.password)


@router.get("/me", response_model=UserOut, summary="Get current user profile")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserOut, summary="Update profile")
def update_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AuthService.update_profile(db, current_user, payload)


@router.post("/logout", summary="Logout (client-side token discard)")
def logout():
    return {"message": "Logged out. Please discard your token on the client."}
