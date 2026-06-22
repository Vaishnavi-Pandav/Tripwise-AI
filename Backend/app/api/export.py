from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.export import TripExportData
from app.services.export_service import ExportService

router = APIRouter(prefix="/trip", tags=["PDF Export"])

@router.post("/export-pdf/{trip_id}", response_model=TripExportData,
             summary="Export complete trip data (PDF-ready JSON)")
def export_trip_pdf(trip_id: str, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    return ExportService.generate_pdf_data(db, trip_id, current_user)
