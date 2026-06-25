from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.settings import UserSettingsOut, UserSettingsUpdate
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["User Settings"])

@router.get("/", response_model=UserSettingsOut, summary="Get user preferences/settings")
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return SettingsService.get_settings(db, current_user)

@router.put("/", response_model=UserSettingsOut, summary="Update user preferences/settings")
def update_settings(payload: UserSettingsUpdate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    return SettingsService.update_settings(db, current_user, payload)
