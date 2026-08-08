from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from ..database import get_db
from ..models import Employee, AttendanceRecord, OfficeLocation, AttendanceMode, SuspiciousCheckIn
from ..services.distance import haversine_distance
from ..services.fraud_detection import FraudDetector
from ..services.audit_logger import AuditLogger

router = APIRouter()

# Request Schema
class CheckInRequest(BaseModel):
    latitude: float
    longitude: float
    gps_accuracy: float
    device_id: str
    ip_address: Optional[str] = None
    mock_location: bool = False

# Response Schema
class CheckInResponse(BaseModel):
    success: bool
    message: str
    distance_meters: Optional[float] = None
    requires_approval: bool = False
    record_id: Optional[int] = None

@router.post("/check-in", response_model=CheckInResponse)
def check_in(request: CheckInRequest, db: Session = Depends(get_db), employee_id: int = 1):
    """
    Employee check-in endpoint
    """
    
    # 1. Validate employee exists
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.is_active == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 2. Check for duplicate check-in (within last 5 minutes)
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_checkin = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.check_in_time >= five_min_ago,
        AttendanceRecord.check_out_time == None
    ).first()

    if recent_checkin:
        raise HTTPException(status_code=400, detail="Already checked in within last 5 minutes")
    
    # 3. Get office location
    office = db.query(OfficeLocation).filter(
        OfficeLocation.id == employee.office_location_id
    ).first()
    
    if not office:
        raise HTTPException(status_code=404, detail="Office location not configured")
    
    # 4. Calculate distance
    distance = haversine_distance(
        office.latitude, office.longitude,
        request.latitude, request.longitude
    )
    
    # 5. Validate based on mode
    is_valid = True
    requires_approval = False
    reason = None

    # CHECK FOR MOCK LOCATION FIRST - AUTO-REJECT
    if request.mock_location == True:
        is_valid = False
        reason = "Mock location detected - GPS spoofing attempted"
        requires_approval = False

    # Office/Field mode validation
    if employee.attendance_mode == AttendanceMode.OFFICE:
        if distance > office.radius_meters:
            is_valid = False
            reason = f"Distance {distance:.2f}m exceeds limit of {office.radius_meters}m"
            requires_approval = True
    elif employee.attendance_mode == AttendanceMode.FIELD:
        if distance > 50000:
            requires_approval = True
            reason = f"Field worker at unusual distance: {distance:.2f}m"

    # GPS accuracy check
    if request.gps_accuracy > 50:
        is_valid = False
        reason = f"GPS accuracy {request.gps_accuracy:.1f}m is poor"
        requires_approval = True

    # 6. Run fraud detection
    fraud_detector = FraudDetector(db)
    fraud_flags = fraud_detector.detect_fraud(
        employee.id,
        request.latitude,
        request.longitude,
        request.gps_accuracy,
        request.device_id,
        request.ip_address or ""
    )

    # If high severity fraud detected, flag for approval
    high_severity_flags = [f for f in fraud_flags if f["severity"] == "high"]
    if high_severity_flags:
        is_valid = False
        requires_approval = True
        reason = high_severity_flags[0]["message"]

    # 7. Save attendance record
    attendance_record = AttendanceRecord(
        employee_id=employee.id,
        check_in_latitude=request.latitude,
        check_in_longitude=request.longitude,
        distance_from_office=distance,
        attendance_mode=employee.attendance_mode,
        is_valid=is_valid,
        device_id=request.device_id,
        ip_address=request.ip_address or "",
        gps_accuracy=request.gps_accuracy,
        is_mock_location=request.mock_location
    )
    
    db.add(attendance_record)
    db.flush()

    # 8. Flag suspicious check-ins
    if not is_valid or requires_approval:
        suspicious = SuspiciousCheckIn(
            attendance_record_id=attendance_record.id,
            reason=reason or "Requires review",
            severity="high" if not is_valid else "medium"
        )
        db.add(suspicious)

    # 9. Log action for audit trail
    AuditLogger.log_check_in(db, employee.id, request.latitude, request.longitude, 
                             is_valid, request.device_id, request.ip_address or "")
    
    db.commit()
    
    return CheckInResponse(
        success=is_valid,
        message="✅ Check-in successful" if is_valid else f"⏳ {reason}",
        distance_meters=round(distance, 2),
        requires_approval=requires_approval,
        record_id=attendance_record.id
    )

@router.post("/check-out", response_model=CheckInResponse)
def check_out(request: CheckInRequest, db: Session = Depends(get_db), employee_id: int = 1):
    """
    Employee check-out endpoint with validation
    """
    
    # 1. Validate employee
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.is_active == True
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # 2. Get latest check-in without check-out
    latest = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.check_out_time == None
    ).order_by(AttendanceRecord.check_in_time.desc()).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No open check-in found")
    
    # 3. Validate check-out location (if office mode)
    office = db.query(OfficeLocation).filter(
        OfficeLocation.id == employee.office_location_id
    ).first()
    
    if employee.attendance_mode == AttendanceMode.OFFICE and office:
        checkout_distance = haversine_distance(
            office.latitude, office.longitude,
            request.latitude, request.longitude
        )
        
        if checkout_distance > office.radius_meters:
            return CheckInResponse(
                success=False,
                message=f"❌ Check-out outside office geofence (distance: {checkout_distance:.2f}m)",
                distance_meters=round(checkout_distance, 2),
                requires_approval=True
            )
    
    # 4. Update check-out time
    latest.check_out_time = datetime.utcnow()
    db.commit()
    
    # 5. Log action
    AuditLogger.log_check_out(db, employee.id, request.latitude, request.longitude, request.device_id)
    
    return CheckInResponse(
        success=True,
        message="✅ Check-out successful",
        distance_meters=round(latest.distance_from_office, 2) if latest.distance_from_office else None,
        record_id=latest.id
    )

@router.get("/history/{employee_id}")
def get_attendance_history(employee_id: int, db: Session = Depends(get_db)):
    """
    Get attendance history for employee (last 30 records)
    """
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id
    ).order_by(AttendanceRecord.check_in_time.desc()).limit(30).all()
    
    return {
        "total": len(records),
        "records": [
            {
                "id": r.id,
                "date": r.check_in_time.strftime("%Y-%m-%d"),
                "check_in": r.check_in_time.strftime("%H:%M"),
                "check_out": r.check_out_time.strftime("%H:%M") if r.check_out_time else None,
                "distance": round(r.distance_from_office, 2) if r.distance_from_office else None,
                "status": "✓ valid" if r.is_valid else "⚠ flagged"
            }
            for r in records
        ]
    }

@router.get("/")
def attendance_root():
    return {"message": "Attendance endpoints available"}

@router.get("/office-locations")
def get_office_locations(db: Session = Depends(get_db)):
    """
    Get all active office locations
    """
    locations = db.query(OfficeLocation).filter(
        OfficeLocation.is_active == True
    ).all()
    
    return {
        "locations": [
            {
                "id": loc.id,
                "name": loc.name,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "radius_meters": loc.radius_meters,
                "city": loc.city
            }
            for loc in locations
        ]
    }