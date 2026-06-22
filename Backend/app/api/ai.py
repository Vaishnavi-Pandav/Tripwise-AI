import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import (
    ChatHistoryListResponse,
    ChatRequest,
    ChatResponse,
    ItineraryResponse,
    TripGenerationRequest,
)
from app.services.ai_service import AIService

logger = logging.getLogger("tripwise")
router = APIRouter(prefix="/ai", tags=["AI Assistant"])

_ai = AIService()


# ── POST /ai/chat ─────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with TripWise AI assistant",
    description="""
Send a travel question to TripWise AI. Optionally pass a `trip_id` to get
context-aware responses based on your specific trip details.

**Without trip context:**
```json
{"message": "What are the best beaches in Goa?"}
```

**With trip context:**
```json
{
  "message": "Can I afford water sports within my budget?",
  "trip_id": "your-trip-uuid"
}
```

The AI will use your trip's destination, budget, days, and travelers to give
a personalised answer.
""",
)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    reply, ctx_used = _ai.generate_response(
        db=db,
        message=payload.message,
        user=current_user,
        trip_id=payload.trip_id,
    )
    return ChatResponse(reply=reply, trip_context_used=ctx_used)


# ── GET /ai/history ───────────────────────────────────────────────────────────

@router.get(
    "/history",
    response_model=ChatHistoryListResponse,
    summary="Get your full AI chat history",
    description="Returns paginated chat history for the authenticated user.",
)
def get_history(
    page:      int = Query(1,  ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _ai.get_chat_history(db, current_user, page=page, page_size=page_size)


# ── GET /ai/history/{trip_id} ─────────────────────────────────────────────────

@router.get(
    "/history/{trip_id}",
    response_model=ChatHistoryListResponse,
    summary="Get AI chat history for a specific trip",
    description="Returns paginated chat history filtered by trip ID.",
)
def get_trip_history(
    trip_id:   str,
    page:      int = Query(1,  ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _ai.get_chat_history(db, current_user, trip_id=trip_id,
                                page=page, page_size=page_size)


# ── POST /ai/generate ─────────────────────────────────────────────────────────
# Public — no login required, used by the frontend Results page

@router.post(
    "/generate",
    response_model=ItineraryResponse,
    summary="Generate a full AI trip itinerary (public)",
    description="""
Generates a complete day-wise Markdown itinerary. **No authentication required.**

```json
{
  "source": "Mumbai",
  "destination": "Goa",
  "days": 4,
  "travelers": 2,
  "budget": 15000
}
```
""",
)
def generate_itinerary(payload: TripGenerationRequest):
    try:
        itinerary = _ai.generate_itinerary(
            source=payload.source,
            destination=payload.destination,
            days=payload.days,
            travelers=payload.travelers,
            budget=payload.budget,
        )
        return ItineraryResponse(itinerary=itinerary)
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


# ── GET /ai/context/{trip_id} ─────────────────────────────────────────────────

@router.get(
    "/context/{trip_id}",
    summary="Preview trip context that AI will use",
    description="Returns the trip context the AI will use for context-aware responses.",
)
def get_trip_context(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ctx = _ai.get_trip_context(db, trip_id, current_user)
    if not ctx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found or does not belong to you",
        )
    return ctx
