from app.database import engine, Base
from app.models import Employee, OfficeLocation, AttendanceRecord, SuspiciousCheckIn
from sqlalchemy import text

# Drop all tables
Base.metadata.drop_all(bind=engine)

# Enable PostGIS extension
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    conn.commit()
    print('✅ PostGIS extension enabled')

# Create all tables
Base.metadata.create_all(bind=engine)
print('✅ Tables recreated successfully with PostGIS support')