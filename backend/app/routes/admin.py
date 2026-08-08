from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..database import get_db
from ..models import SuspiciousCheckIn, AttendanceRecord

router = APIRouter()

class AdminActionRequest(BaseModel):
    notes: Optional[str] = None

@router.get("/suspicious-checkins")
def get_suspicious_checkins(
    db: Session = Depends(get_db),
    limit: int = 50,
    admin_id: int = 2
):
    """
    Get all flagged check-ins pending admin review.
    Intended to be accessed from the Admin role in the UI (no server-side
    authentication - this project uses a UI-only role toggle, see README).
    """

    flags = db.query(SuspiciousCheckIn).filter(
        SuspiciousCheckIn.admin_reviewed == False
    ).order_by(SuspiciousCheckIn.flagged_at.desc()).limit(limit).all()

    return {
        "count": len(flags),
        "records": [
            {
                "id": f.id,
                "attendance_record_id": f.attendance_record_id,
                "reason": f.reason,
                "severity": f.severity,
                "flagged_at": f.flagged_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "pending"
            }
            for f in flags
        ]
    }

@router.post("/approve/{suspicious_id}")
def approve_checkin(
    suspicious_id: int,
    request: AdminActionRequest,
    db: Session = Depends(get_db),
    admin_id: int = 2
):
    """
    Approve a flagged check-in.
    """

    suspicious = db.query(SuspiciousCheckIn).filter(
        SuspiciousCheckIn.id == suspicious_id
    ).first()

    if not suspicious:
        raise HTTPException(status_code=404, detail="Record not found")

    # Update suspicious record
    suspicious.admin_reviewed = True
    suspicious.admin_decision = "approved"
    suspicious.admin_notes = request.notes or ""
    suspicious.reviewed_at = datetime.utcnow()

    # Mark attendance record as valid
    attendance = db.query(AttendanceRecord).filter(
        AttendanceRecord.id == suspicious.attendance_record_id
    ).first()

    if attendance:
        attendance.is_valid = True

    db.commit()

    return {
        "success": True,
        "message": "✅ Check-in approved",
        "id": suspicious_id
    }

@router.post("/reject/{suspicious_id}")
def reject_checkin(
    suspicious_id: int,
    request: AdminActionRequest,
    db: Session = Depends(get_db),
    admin_id: int = 2
):
    """
    Reject a flagged check-in.
    """

    suspicious = db.query(SuspiciousCheckIn).filter(
        SuspiciousCheckIn.id == suspicious_id
    ).first()

    if not suspicious:
        raise HTTPException(status_code=404, detail="Record not found")

    # Update suspicious record
    suspicious.admin_reviewed = True
    suspicious.admin_decision = "rejected"
    suspicious.admin_notes = request.notes or ""
    suspicious.reviewed_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": "❌ Check-in rejected",
        "id": suspicious_id
    }

@router.get("/")
def admin_root():
    return {"message": "Admin endpoints available"}
