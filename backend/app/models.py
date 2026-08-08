from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class AttendanceMode(enum.Enum):
    OFFICE = "office"
    FIELD = "field"

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    employee_id = Column(String, unique=True, index=True)
    attendance_mode = Column(Enum(AttendanceMode), default=AttendanceMode.OFFICE)
    office_location_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    attendance_records = relationship("AttendanceRecord", back_populates="employee")

class OfficeLocation(Base):
    __tablename__ = "office_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    radius_meters = Column(Integer, default=100)
    city = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), index=True)
    check_in_time = Column(DateTime, default=datetime.utcnow)
    check_in_latitude = Column(Float)
    check_in_longitude = Column(Float)
    check_out_time = Column(DateTime, nullable=True)
    distance_from_office = Column(Float, nullable=True)
    attendance_mode = Column(Enum(AttendanceMode))
    is_valid = Column(Boolean, default=True)
    device_id = Column(String)
    ip_address = Column(String, nullable=True)
    gps_accuracy = Column(Float)
    is_mock_location = Column(Boolean, default=False)
    check_out_latitude = Column(Float, nullable=True)
    check_out_longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    employee = relationship("Employee", back_populates="attendance_records")
    suspicious_flags = relationship("SuspiciousCheckIn", back_populates="attendance_record")

class SuspiciousCheckIn(Base):
    __tablename__ = "suspicious_check_ins"

    id = Column(Integer, primary_key=True, index=True)
    attendance_record_id = Column(Integer, ForeignKey("attendance_records.id"), index=True)
    reason = Column(String)
    severity = Column(String)  # 'low', 'medium', 'high'
    flagged_at = Column(DateTime, default=datetime.utcnow)
    admin_reviewed = Column(Boolean, default=False)
    admin_decision = Column(String, nullable=True)  # 'approved', 'rejected'
    admin_notes = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    attendance_record = relationship("AttendanceRecord", back_populates="suspicious_flags")
