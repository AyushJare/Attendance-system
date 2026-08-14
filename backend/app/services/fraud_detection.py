from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import AttendanceRecord
from ..services.distance import haversine_distance

class FraudDetector:
    def __init__(self, db: Session):
        self.db = db

    def detect_fraud(self, employee_id, latitude, longitude, accuracy, device_id, ip_address):
        """Detect fraud including velocity analysis"""
        flags = []
        
        # GPS accuracy check
        if accuracy > 50:
            flags.append({
                "message": f"Poor GPS accuracy: {accuracy:.1f}m",
                "severity": "medium"
            })
        
        # Velocity check - detect impossible travel
        last_checkin = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.check_in_time.isnot(None)
        ).order_by(AttendanceRecord.check_in_time.desc()).first()
        
        if last_checkin:
            from datetime import datetime
            current_time = datetime.utcnow()
            time_delta = (current_time - last_checkin.check_in_time).total_seconds()
            
            # Extract lat/lon from PostGIS geometry
            if last_checkin.check_in_location:
                # Use SQL functions to extract coordinates
                result = self.db.query(
                    func.ST_Y(last_checkin.check_in_location).label('lat'),
                    func.ST_X(last_checkin.check_in_location).label('lon')
                ).first()
                
                if result:
                    prev_lat = result.lat
                    prev_lon = result.lon
                    
                    distance = haversine_distance(
                        prev_lat, prev_lon,
                        latitude, longitude
                    )
                    
                    # Check for impossible travel (>250 m/s = aircraft speed)
                    if time_delta > 0:
                        actual_speed_ms = distance / time_delta
                        if actual_speed_ms > 250:
                            distance_km = distance / 1000
                            hours = time_delta / 3600
                            speed_kmh = (distance_km / hours) if hours > 0 else 0
                            
                            flags.append({
                                "message": f"Impossible travel: {distance_km:.1f}km in {hours:.2f}h ({speed_kmh:.0f} km/h)",
                                "severity": "high"
                            })
        
        return flags