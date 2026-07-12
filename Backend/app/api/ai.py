import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_current_user_optional
from app.core.rate_limit import limiter
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


# ── POST /ai/chat — public, optionally authenticated ──────────────────────────

@router.post("/chat", response_model=ChatResponse, summary="Chat with TripWise AI")
@limiter.limit("10/minute")
def chat(
    request: Request,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Chat with TripWise AI."""
    if not payload.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty")
    try:
        if current_user:
            reply, context_used = _ai.generate_response(db, payload.message, current_user, payload.trip_id)
            return ChatResponse(reply=reply, trip_context_used=context_used)
        else:
            # Pass db so RAG + tools work for unauthenticated users too
            reply = _ai.chat(payload.message, db=db)
            return ChatResponse(reply=reply, trip_context_used=False)
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
@limiter.limit("5/minute")
def generate_itinerary(request: Request, payload: TripGenerationRequest):
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


# ── DELETE /ai/memory — clear conversation memory ─────────────────────────────

@router.delete("/memory", summary="Clear conversation memory")
def clear_memory(current_user: User = Depends(get_current_user)):
    """Clear the in-memory conversation history for the current user."""
    AIService.clear_memory(str(current_user.id))
    return {"message": "Conversation memory cleared."}


# ── GET /ai/memory — preview current memory ────────────────────────────────────

@router.get("/memory", summary="Preview conversation memory")
def get_memory(current_user: User = Depends(get_current_user)):
    """Return the current in-memory conversation history (last 5 exchanges)."""
    history = AIService.get_memory_preview(str(current_user.id))
    return {"memory": history, "count": len(history)}


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
