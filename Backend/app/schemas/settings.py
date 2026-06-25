from typing import Optional
from pydantic import BaseModel

class UserSettingsOut(BaseModel):
    preferred_budget: Optional[str]
    travel_styles: Optional[list]
    preferred_climates: Optional[list]
    dietary_needs: Optional[list]

class UserSettingsUpdate(BaseModel):
    preferred_budget: Optional[str] = None
    travel_styles: Optional[list] = None
    preferred_climates: Optional[list] = None
    dietary_needs: Optional[list] = None
