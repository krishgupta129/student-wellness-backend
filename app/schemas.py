from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
try:
    from app.models import HabitType, GroupRole
except ImportError:
    from models import HabitType, GroupRole


# User schemas
class UserOut(BaseModel):
    uid: str
    email: Optional[str] = None
    displayName: Optional[str] = None
    photoUrl: Optional[str] = None
    createdAt: Optional[datetime] = None

# Habit schemas
class HabitLogIn(BaseModel):
    habit_type: HabitType
    value: float = Field(gt=0, description="Must be greater than 0")
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None

class HabitLogOut(BaseModel):
    id: str
    uid: str
    habit_type: HabitType
    value: float
    unit: str
    timestamp: datetime

class StreakOut(BaseModel):
    habit_type: HabitType
    current_streak: int
    best_streak: int
    updated_at: datetime

# Group schemas
class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class GroupJoin(BaseModel):
    join_code: str = Field(min_length=6, max_length=6)

class GroupOut(BaseModel):
    id: str
    name: str
    join_code: str
    owner_id: str
    created_at: datetime
    member_count: Optional[int] = None

class GroupMember(BaseModel):
    user_id: str
    display_name: Optional[str] = None
    role: GroupRole
    consistency_score: Optional[float] = None

class GroupLeaderboard(BaseModel):
    group_id: str
    group_name: str
    members: List[GroupMember]
    week_start: datetime

# Response schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True
