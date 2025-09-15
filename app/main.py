from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import routers
from routers import auth, habits, groups

# Create FastAPI app
app = FastAPI(
    title="Student Wellness API",
    description="Backend API for student wellness tracking with habits, streaks, and group challenges",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Student Wellness API is running successfully!",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "auth": "/auth",
            "habits": "/habits", 
            "groups": "/groups"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-09-15"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(habits.router, prefix="/habits", tags=["Habits"])
app.include_router(groups.router, prefix="/groups", tags=["Groups"])

# Root endpoint for API info
@app.get("/api/info")
async def api_info():
    return {
        "api_name": "Student Wellness Backend",
        "version": "1.0.0",
        "features": [
            "User Authentication with Firebase",
            "Habit Logging and Tracking", 
            "Streak Calculation",
            "Group Challenges",
            "Leaderboards"
        ]
    }
