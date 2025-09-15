from enum import Enum
from typing import List, Optional
from datetime import datetime

# Allowed habit types
class HabitType(str, Enum):
    SLEEP = "sleep"
    EXERCISE = "exercise" 
    WATER = "water"
    STUDY = "study"

# User roles in groups
class GroupRole(str, Enum):
    OWNER = "owner"
    MEMBER = "member"

# Constants
HABIT_UNITS = {
    HabitType.SLEEP: "hours",
    HabitType.EXERCISE: "minutes", 
    HabitType.WATER: "glasses",
    HabitType.STUDY: "hours"
}

# Helper functions
def generate_join_code() -> str:
    """Generate a random 6-character join code for groups"""
    import random
    import string
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

def get_default_unit(habit_type: HabitType) -> str:
    """Get default unit for a habit type"""
    return HABIT_UNITS.get(habit_type, "units")
