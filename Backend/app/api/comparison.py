from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.comparison import CompareOut, CompareRequest
from app.services.comparison_service import ComparisonService

router = APIRouter(prefix="/compare-destinations", tags=["Destination Comparison"])

_svc = ComparisonService()


@router.post("/", response_model=CompareOut, summary="Compare two destinations")
def compare_destinations(
    payload: CompareRequest,
    current_user: User = Depends(get_current_user),
):
    return _svc.compare(payload.destination1, payload.destination2)
