import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class HiddenGem(Base):
    __tablename__ = "hidden_gems"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city             = Column(String(150), nullable=False, index=True)
    place_name       = Column(String(255), nullable=False)
    description      = Column(Text, nullable=True)
    recommended_for  = Column(String(255), nullable=True)   # solo | couples | families | adventure
    image_url        = Column(Text, nullable=True)
