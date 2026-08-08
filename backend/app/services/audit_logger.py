from datetime import datetime
from sqlalchemy.orm import Session
from ..models import AttendanceRecord

class AuditLogger:
    """Log all attendance actions for compliance"""
    
    @staticmethod
    def log_check_in(db: Session, employee_id: int, latitude: float, longitude: float, 
                     is_valid: bool, device_id: str, ip_address: str):
        """Log check-in action"""
        log_entry = f"[{datetime.utcnow().isoformat()}] CHECKIN | Employee: {employee_id} | Location: ({latitude}, {longitude}) | Valid: {is_valid} | Device: {device_id} | IP: {ip_address}"
        
        # In production, this would write to a dedicated audit log file/database
        print(f"AUDIT: {log_entry}")
        
        # Could also store in database:
        # audit_record = AuditLog(action='CHECK_IN', employee_id=employee_id, details=log_entry)
        # db.add(audit_record)
        # db.commit()
    
    @staticmethod
    def log_check_out(db: Session, employee_id: int, latitude: float, longitude: float, device_id: str):
        """Log check-out action"""
        log_entry = f"[{datetime.utcnow().isoformat()}] CHECKOUT | Employee: {employee_id} | Location: ({latitude}, {longitude}) | Device: {device_id}"
        
        print(f"AUDIT: {log_entry}")
    
    @staticmethod
    def log_admin_action(db: Session, admin_id: int, action: str, target_id: int, notes: str = ""):
        """Log admin approval/rejection"""
        log_entry = f"[{datetime.utcnow().isoformat()}] ADMIN_{action} | Admin: {admin_id} | Target: {target_id} | Notes: {notes}"
        
        print(f"AUDIT: {log_entry}")