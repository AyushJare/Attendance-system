from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .database import engine, Base
from .models import Employee, OfficeLocation, AttendanceRecord
from .routes import attendance, admin

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Attendance Tracking API",
    description="Location-based attendance system",
    version="1.0.0"
)

def is_localhost(origin: str) -> bool:
    return origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["attendance"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {
        "message": "Attendance Tracking API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
