from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse, ItineraryResponse, TripGenerationRequest
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

_ai = AIService()


@router.post("/chat", response_model=ChatResponse, summary="Chat with TripWise AI assistant")
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to the AI travel assistant.
    Example: `{"message": "Suggest a Goa trip under ₹15000"}`
    """
    try:
        reply = _ai.chat(payload.message)
        return ChatResponse(reply=reply)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.post("/generate", response_model=ItineraryResponse, summary="Generate AI trip itinerary")
def generate(payload: TripGenerationRequest):
    """
    Public endpoint — no login required.
    Accepts trip details and returns a full markdown itinerary.

    Example:
    ```json
    {
      "source": "Mumbai",
      "destination": "Goa",
      "days": 4,
      "travelers": 2,
      "budget": 15000
    }
    ```
    """
    try:
        itinerary = _ai.generate_itinerary(
            source=payload.source,
            destination=payload.destination,
            days=payload.days,
            travelers=payload.travelers,
            budget=payload.budget,
        )
        return ItineraryResponse(itinerary=itinerary)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
