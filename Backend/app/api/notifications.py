from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationListResponse, NotificationOut
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=NotificationListResponse, summary="Get all notifications")
def get_notifications(unread_only: bool = Query(False),
                      db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return NotificationService.get_all(db, current_user, unread_only)

@router.put("/{notification_id}/read", response_model=NotificationOut, summary="Mark notification as read")
def mark_read(notification_id: str, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    return NotificationService.mark_read(db, current_user, notification_id)

@router.put("/read-all", summary="Mark all notifications as read")
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = NotificationService.mark_all_read(db, current_user)
    return {"marked_read": count}
