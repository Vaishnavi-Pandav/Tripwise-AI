import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.settings import UserSettingsOut, UserSettingsUpdate
from app.services.settings_service import SettingsService

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/settings", tags=["User Settings"])


@router.get(
    "",
    response_model=UserSettingsOut,
    summary="Get user settings / preferences",
    description=(
        "Retrieve travel preferences for the authenticated user. "
        "If no preferences exist, default empty settings are created and returned."
    ),
)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SettingsService.get_settings(db, current_user)


@router.put(
    "",
    response_model=UserSettingsOut,
    summary="Update user settings / preferences",
    description=(
        "Update travel preferences. Only the provided fields are changed. "
        "Creates the preferences record if it doesn't exist yet."
    ),
)
def update_settings(
    payload: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SettingsService.update_settings(db, current_user, payload)
