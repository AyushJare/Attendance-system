from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import AttendanceRecord
from .distance import haversine_distance

class FraudDetector:
    def __init__(self, db: Session):
        self.db = db
        self.MAX_SPEED_KM_PER_HOUR = 100
        self.MIN_GPS_ACCURACY = 50  # meters
        self.MIN_TIME_BETWEEN_CHECKINS = 5  # minutes

    def detect_fraud(self, employee_id: int, latitude: float, longitude: float,
                    gps_accuracy: float, device_id: str, ip_address: str) -> list:
        """
        Run all fraud detection checks.
        Returns list of flagged issues with severity.
        """
        flags = []

        # 1. GPS Accuracy Check
        if gps_accuracy > self.MIN_GPS_ACCURACY:
            flags.append({
                "type": "poor_gps",
                "severity": "medium",
                "message": f"GPS accuracy: {gps_accuracy:.1f}m (threshold: {self.MIN_GPS_ACCURACY}m)"
            })

        # 2. Impossible Speed Check
        last_checkin = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.is_valid == True
        ).order_by(AttendanceRecord.check_in_time.desc()).first()

        if last_checkin:
            time_diff_minutes = (datetime.utcnow() - last_checkin.check_in_time).total_seconds() / 60

            if time_diff_minutes > 0:
                distance = haversine_distance(
                    last_checkin.check_in_latitude,
                    last_checkin.check_in_longitude,
                    latitude,
                    longitude
                )

                speed_kmh = (distance / 1000) / (time_diff_minutes / 60) if time_diff_minutes > 0 else 0

                if speed_kmh > self.MAX_SPEED_KM_PER_HOUR:
                    flags.append({
                        "type": "impossible_speed",
                        "severity": "high",
                        "message": f"Speed: {speed_kmh:.2f} km/h (limit: {self.MAX_SPEED_KM_PER_HOUR})"
                    })

        # 3. Duplicate Check-in (< 5 minutes)
        recent_checkin = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.check_in_time >= datetime.utcnow() - timedelta(minutes=self.MIN_TIME_BETWEEN_CHECKINS)
        ).first()

        if recent_checkin:
            flags.append({
                "type": "duplicate_checkin",
                "severity": "high",
                "message": f"Already checked in within {self.MIN_TIME_BETWEEN_CHECKINS} minutes"
            })

        return flags
