from fastapi import APIRouter, HTTPException, status

from app.schemas.ai import ItineraryResponse, TripGenerationRequest
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["AI"])

_ai_service = AIService()


@router.post(
    "/generate",
    response_model=ItineraryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a full AI travel itinerary",
)
def generate_itinerary(payload: TripGenerationRequest):
    """Calls GPT-4o-mini with trip details and returns a markdown itinerary."""
    try:
        itinerary = _ai_service.generate_itinerary(
            source=payload.source,
            destination=payload.destination,
            days=payload.days,
            travelers=payload.travelers,
            budget=payload.budget,
        )
        return ItineraryResponse(itinerary=itinerary)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
