from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsDashboardOut
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Analytics Dashboard"])

@router.get("/analytics", response_model=AnalyticsDashboardOut, summary="Get travel analytics dashboard")
def get_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AnalyticsService.get_dashboard(db, current_user)
