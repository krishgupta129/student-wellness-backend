import random
import string
from datetime import datetime, timedelta, date
from typing import List, Set
try:
    from app.models import HabitType
except ImportError:
    from models import HabitType


def generate_join_code() -> str:
    """Generate a random 6-character join code for groups"""
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

def get_date_range(days: int) -> datetime:
    """Get datetime from N days ago"""
    return datetime.utcnow() - timedelta(days=days)

def compute_streak(habit_dates: List[date]) -> tuple[int, int]:
    """
    Compute current streak and best streak from a list of habit dates
    Returns: (current_streak, best_streak)
    """
    if not habit_dates:
        return 0, 0
    
    # Convert to set for O(1) lookup and sort
    date_set = set(habit_dates)
    today = date.today()
    
    # Calculate current streak
    current_streak = 0
    check_date = today
    while check_date in date_set:
        current_streak += 1
        check_date -= timedelta(days=1)
    
    # Calculate best streak
    sorted_dates = sorted(date_set)
    best_streak = 0
    current_run = 1
    
    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] == sorted_dates[i-1] + timedelta(days=1):
            current_run += 1
        else:
            best_streak = max(best_streak, current_run)
            current_run = 1
    
    best_streak = max(best_streak, current_run)
    
    return current_streak, best_streak

def get_default_unit(habit_type: HabitType) -> str:
    """Get default unit for a habit type"""
    units = {
        HabitType.SLEEP: "hours",
        HabitType.EXERCISE: "minutes", 
        HabitType.WATER: "glasses",
        HabitType.STUDY: "hours"
    }
    return units.get(habit_type, "units")
