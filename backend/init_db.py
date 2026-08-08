from app.database import engine, Base
from app.models import Employee, OfficeLocation, AttendanceRecord, SuspiciousCheckIn

# Drop all tables
Base.metadata.drop_all(bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)
print('✅ Tables recreated successfully')