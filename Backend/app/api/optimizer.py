from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.optimizer import BudgetOptimizeResponse
from app.services.optimizer_service import OptimizerService

router = APIRouter(prefix="/budget", tags=["AI Budget Optimizer"])

@router.post("/ai-optimize", response_model=BudgetOptimizeResponse,
             summary="AI-powered budget optimization for a trip")
def ai_optimize(trip_id: str, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return OptimizerService.optimize(db, trip_id, current_user)
