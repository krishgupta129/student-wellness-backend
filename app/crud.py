from datetime import datetime, date
from typing import List, Optional, Dict, Any
from google.cloud import firestore
# Handle imports for different execution contexts
try:
    from app.database import get_db
    from app.utils import generate_join_code, compute_streak, get_default_unit
    from app.models import HabitType, GroupRole
except ImportError:
    from database import get_db
    from utils import generate_join_code, compute_streak, get_default_unit
    from models import HabitType, GroupRole


db = get_db()

# User CRUD operations
async def create_or_update_user(uid: str, email: str = None, display_name: str = None, photo_url: str = None) -> Dict[str, Any]:
    """Create or update user in Firestore"""
    user_ref = db.collection("users").document(uid)
    user_data = {
        "uid": uid,
        "email": email,
        "displayName": display_name,
        "photoUrl": photo_url,
        "updatedAt": firestore.SERVER_TIMESTAMP
    }
    
    # Only set createdAt if it's a new user
    user_doc = user_ref.get()
    if not user_doc.exists:
        user_data["createdAt"] = firestore.SERVER_TIMESTAMP
    
    user_ref.set(user_data, merge=True)
    return user_data

# Habit CRUD operations
async def add_habit_log(uid: str, habit_type: HabitType, value: float, unit: str = None, timestamp: datetime = None) -> str:
    """Add a habit log entry"""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    if unit is None:
        unit = get_default_unit(habit_type)
    
    log_data = {
        "uid": uid,
        "habitType": habit_type.value,
        "value": value,
        "unit": unit,
        "timestamp": timestamp,
        "createdAt": firestore.SERVER_TIMESTAMP
    }
    
    doc_ref = db.collection("habit_logs").add(log_data)
    return doc_ref[1].id

async def get_habit_logs(uid: str, habit_type: HabitType = None, days: int = 7) -> List[Dict[str, Any]]:
    """Get habit logs for a user"""
    query = db.collection("habit_logs").where("uid", "==", uid)
    
    if habit_type:
        query = query.where("habitType", "==", habit_type.value)
    
    # Get logs from last N days
    start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = start_date.replace(day=start_date.day - days)
    query = query.where("timestamp", ">=", start_date)
    
    docs = query.order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    
    logs = []
    for doc in docs:
        log_data = doc.to_dict()
        log_data["id"] = doc.id
        logs.append(log_data)
    
    return logs

async def get_streak(uid: str, habit_type: HabitType) -> Dict[str, Any]:
    """Calculate streak for a habit"""
    # Get all logs for this habit (limit to last 60 days for performance)
    start_date = datetime.utcnow().replace(day=datetime.utcnow().day - 60)
    
    query = (db.collection("habit_logs")
             .where("uid", "==", uid)
             .where("habitType", "==", habit_type.value)
             .where("timestamp", ">=", start_date)
             .order_by("timestamp"))
    
    docs = query.stream()
    
    # Extract dates (convert datetime to date)
    habit_dates = []
    for doc in docs:
        log_data = doc.to_dict()
        log_date = log_data["timestamp"].date() if hasattr(log_data["timestamp"], 'date') else log_data["timestamp"]
        habit_dates.append(log_date)
    
    # Remove duplicates and compute streaks
    unique_dates = list(set(habit_dates))
    current_streak, best_streak = compute_streak(unique_dates)
    
    return {
        "habit_type": habit_type.value,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "updated_at": datetime.utcnow()
    }

# Group CRUD operations
async def create_group(name: str, owner_id: str) -> Dict[str, Any]:
    """Create a new group"""
    join_code = generate_join_code()
    
    group_data = {
        "name": name,
        "ownerId": owner_id,
        "joinCode": join_code,
        "createdAt": firestore.SERVER_TIMESTAMP
    }
    
    # Create group document
    group_ref = db.collection("groups").document()
    group_ref.set(group_data)
    
    # Add owner as first member
    member_data = {
        "groupId": group_ref.id,
        "userId": owner_id,
        "role": GroupRole.OWNER.value,
        "joinedAt": firestore.SERVER_TIMESTAMP
    }
    
    db.collection("group_members").document(f"{group_ref.id}_{owner_id}").set(member_data)
    
    group_data["id"] = group_ref.id
    return group_data

async def join_group(join_code: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Join a group by join code"""
    # Find group by join code
    groups = db.collection("groups").where("joinCode", "==", join_code).limit(1).stream()
    
    group_doc = next(groups, None)
    if not group_doc:
        return None
    
    group_id = group_doc.id
    
    # Add user as member
    member_data = {
        "groupId": group_id,
        "userId": user_id,
        "role": GroupRole.MEMBER.value,
        "joinedAt": firestore.SERVER_TIMESTAMP
    }
    
    db.collection("group_members").document(f"{group_id}_{user_id}").set(member_data, merge=True)
    
    group_data = group_doc.to_dict()
    group_data["id"] = group_id
    return group_data
