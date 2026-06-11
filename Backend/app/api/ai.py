from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse
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
