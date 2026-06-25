from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel

EntityType = Literal["destination","hotel","trip","package"]

class FavoriteCreate(BaseModel):
    entity_id: str

class FavoriteOut(BaseModel):
    id: str
    user_id: str
    entity_type: str
    entity_id: str
    created_at: datetime
    model_config = {"from_attributes": True}
