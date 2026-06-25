import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationListResponse

logger = logging.getLogger("tripwise")

class NotificationService:
    @staticmethod
    def get_all(db: Session, user: User, unread_only: bool = False) -> NotificationListResponse:
        q = db.query(Notification).filter(Notification.user_id == user.id)
        if unread_only:
            q = q.filter(Notification.is_read == False)
        records = q.order_by(Notification.created_at.desc()).limit(50).all()
        total  = db.query(Notification).filter(Notification.user_id == user.id).count()
        unread = db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).count()
        return NotificationListResponse(notifications=records, total=total, unread=unread)

    @staticmethod
    def mark_read(db: Session, user: User, notification_id: str) -> Notification:
        n = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user.id).first()
        if not n:
            raise HTTPException(status_code=404, detail="Notification not found")
        n.is_read = True; db.commit(); db.refresh(n)
        return n

    @staticmethod
    def create_notification(db: Session, user_id: str, title: str, message: str, ntype: str) -> Notification:
        n = Notification(user_id=user_id, title=title, message=message, notification_type=ntype)
        db.add(n); db.commit(); db.refresh(n)
        return n

    @staticmethod
    def mark_all_read(db: Session, user: User) -> int:
        count = db.query(Notification).filter(
            Notification.user_id == user.id, Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        return count
