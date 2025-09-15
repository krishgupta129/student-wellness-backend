from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import HabitLogIn, HabitLogOut, StreakOut, MessageResponse
from crud import add_habit_log, get_habit_logs, get_streak
from models import HabitType
from routers.auth import get_current_user

router = APIRouter()

@router.post("/log", response_model=MessageResponse)
async def log_habit(
    habit_data: HabitLogIn,
    current_user = Depends(get_current_user)
):
    """Log a new habit entry"""
    try:
        log_id = await add_habit_log(
            uid=current_user["uid"],
            habit_type=habit_data.habit_type,
            value=habit_data.value,
            unit=habit_data.unit,
            timestamp=habit_data.timestamp
        )
        
        return MessageResponse(
            message=f"Habit logged successfully with ID: {log_id}",
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to log habit: {str(e)}"
        )

@router.get("/logs")
async def get_habits(
    habit_type: Optional[HabitType] = Query(None, description="Filter by habit type"),
    days: int = Query(7, ge=1, le=365, description="Number of days to retrieve"),
    current_user = Depends(get_current_user)
):
    """Get habit logs for the current user"""
    try:
        logs = await get_habit_logs(
            uid=current_user["uid"],
            habit_type=habit_type,
            days=days
        )
        
        return {
            "logs": logs,
            "total_count": len(logs),
            "days_requested": days,
            "habit_type": habit_type.value if habit_type else "all"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve habits: {str(e)}"
        )

@router.get("/streak/{habit_type}", response_model=StreakOut)
async def get_habit_streak(
    habit_type: HabitType,
    current_user = Depends(get_current_user)
):
    """Get streak information for a specific habit"""
    try:
        streak_data = await get_streak(
            uid=current_user["uid"],
            habit_type=habit_type
        )
        
        return StreakOut(
            habit_type=habit_type,
            current_streak=streak_data["current_streak"],
            best_streak=streak_data["best_streak"],
            updated_at=streak_data["updated_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get streak: {str(e)}"
        )

@router.get("/summary")
async def get_habits_summary(
    days: int = Query(7, ge=1, le=30, description="Number of days for summary"),
    current_user = Depends(get_current_user)
):
    """Get a summary of all habits for the user"""
    try:
        summary = {}
        
        # Get data for each habit type
        for habit_type in HabitType:
            logs = await get_habit_logs(
                uid=current_user["uid"],
                habit_type=habit_type,
                days=days
            )
            
            streak_data = await get_streak(
                uid=current_user["uid"],
                habit_type=habit_type
            )
            
            summary[habit_type.value] = {
                "total_entries": len(logs),
                "current_streak": streak_data["current_streak"],
                "best_streak": streak_data["best_streak"],
                "recent_logs": logs[:5]  # Last 5 entries
            }
        
        return {
            "summary": summary,
            "days_covered": days,
            "user_id": current_user["uid"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get summary: {str(e)}"
        )
