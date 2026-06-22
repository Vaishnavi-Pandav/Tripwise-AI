import json
import logging
from sqlalchemy.orm import Session
from app.models.user_preferences import UserPreferences
from app.models.user import User
from app.schemas.settings import UserSettingsOut, UserSettingsUpdate

logger = logging.getLogger("tripwise")

def _parse(v) -> list:
    if not v: return []
    if isinstance(v, list): return v
    try: return json.loads(v)
    except: return []

class SettingsService:
    @staticmethod
    def get_settings(db: Session, user: User) -> UserSettingsOut:
        prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        if not prefs:
            return UserSettingsOut(preferred_budget=None, travel_styles=[], preferred_climates=[], dietary_needs=[])
        return UserSettingsOut(
            preferred_budget=prefs.preferred_budget,
            travel_styles=_parse(prefs.travel_styles),
            preferred_climates=_parse(prefs.preferred_climates),
            dietary_needs=_parse(prefs.dietary_needs),
        )

    @staticmethod
    def update_settings(db: Session, user: User, payload: UserSettingsUpdate) -> UserSettingsOut:
        prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        if not prefs:
            prefs = UserPreferences(user_id=user.id)
            db.add(prefs)
        if payload.preferred_budget is not None:
            prefs.preferred_budget = payload.preferred_budget
        if payload.travel_styles is not None:
            prefs.travel_styles = json.dumps(payload.travel_styles)
        if payload.preferred_climates is not None:
            prefs.preferred_climates = json.dumps(payload.preferred_climates)
        if payload.dietary_needs is not None:
            prefs.dietary_needs = json.dumps(payload.dietary_needs)
        db.commit(); db.refresh(prefs)
        return SettingsService.get_settings(db, user)
