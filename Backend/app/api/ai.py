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


# ── POST /ai/chat — requires authentication ────────────────────────────────────

@router.post("/chat", response_model=ChatResponse, summary="Chat with TripWise AI (auth required)")
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to TripWise AI. User must be logged in."""
    if not payload.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty")
    try:
        reply, ctx_used = _ai.generate_response(
            db=db, message=payload.message,
            user=current_user, trip_id=payload.trip_id,
        )
        return ChatResponse(reply=reply, trip_context_used=ctx_used)
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


# ── GET /ai/history ────────────────────────────────────────────────────────────

@router.get("/history", response_model=ChatHistoryListResponse, summary="Get chat history")
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _ai.get_chat_history(db, current_user, page=page, page_size=page_size)


# ── GET /ai/history/{trip_id} ─────────────────────────────────────────────────

@router.get("/history/{trip_id}", response_model=ChatHistoryListResponse, summary="Trip chat history")
def get_trip_history(
    trip_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _ai.get_chat_history(db, current_user, trip_id=trip_id, page=page, page_size=page_size)


# ── POST /ai/generate — PUBLIC (no auth needed for frontend form) ─────────────

@router.post("/generate", response_model=ItineraryResponse, summary="Generate AI itinerary (public)")
def generate_itinerary(payload: TripGenerationRequest):
    try:
        itinerary = _ai.generate_itinerary(
            source=payload.source, destination=payload.destination,
            days=payload.days, travelers=payload.travelers, budget=payload.budget,
        )
        return ItineraryResponse(itinerary=itinerary)
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


# ── GET /ai/context/{trip_id} ─────────────────────────────────────────────────

@router.get("/context/{trip_id}", summary="Preview trip context for AI")
def get_trip_context(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ctx = _ai.get_trip_context(db, trip_id, current_user)
    if not ctx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return ctx
