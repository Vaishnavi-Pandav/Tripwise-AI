from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NotificationOut(BaseModel):
    id: str
    title: str
    message: str
    notification_type: Optional[str]
    is_read: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class NotificationListResponse(BaseModel):
    notifications: list[NotificationOut]
    total: int
    unread: int
