from app.database import SessionLocal
from app.models import Employee, OfficeLocation, AttendanceRecord, SuspiciousCheckIn, AttendanceMode
from geoalchemy2.elements import WKTElement

def create_test_data():
    db = SessionLocal()

    # Create office location using PostGIS geometry
    mumbai_office = OfficeLocation(
        id=1, 
        name="Mumbai Office", 
        location=WKTElement('POINT(72.8777 19.0760)', srid=4326),  # longitude, latitude
        radius_meters=100, 
        city="Mumbai"
    )
    db.add(mumbai_office)
    db.flush()

    # Create test employees
    employee = Employee(
        id=1, 
        email="employee@test.com", 
        name="Employee User", 
        employee_id="EMP001",
        attendance_mode=AttendanceMode.OFFICE, 
        office_location_id=1,
        is_admin=False,  # Normal employee
        is_active=True
    )
    
    admin = Employee(
        id=2, 
        email="admin@test.com", 
        name="Admin User", 
        employee_id="ADMIN001",
        attendance_mode=AttendanceMode.OFFICE, 
        office_location_id=1,
        is_admin=True,  # Admin user
        is_active=True
    )
    
    db.add_all([employee, admin])
    db.commit()
    
    print("✅ Test data created successfully!")
    print("\n📊 CREATED DATA:")
    print("   Office: Mumbai (19.0760°N, 72.8777°E)")
    print("   Radius: 100m")
    print("\n👥 EMPLOYEES:")
    print("   1. Employee User (ID: 1) - Regular Employee")
    print("   2. Admin User (ID: 2) - Admin User")
    print("\n✅ Ready to test!")
    
    db.close()

if __name__ == "__main__":
    create_test_data()