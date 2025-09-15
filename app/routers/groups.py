from fastapi import APIRouter, Depends, HTTPException
from typing import List
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import GroupCreate, GroupJoin, GroupOut, MessageResponse
from crud import create_group, join_group
from routers.auth import get_current_user

router = APIRouter()

@router.post("/create", response_model=GroupOut)
async def create_wellness_group(
    group_data: GroupCreate,
    current_user = Depends(get_current_user)
):
    """Create a new wellness group"""
    try:
        group = await create_group(
            name=group_data.name,
            owner_id=current_user["uid"]
        )
        
        return GroupOut(
            id=group["id"],
            name=group["name"],
            join_code=group["joinCode"],
            owner_id=group["ownerId"],
            created_at=group.get("createdAt"),
            member_count=1
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create group: {str(e)}"
        )

@router.post("/join", response_model=MessageResponse)
async def join_wellness_group(
    join_data: GroupJoin,
    current_user = Depends(get_current_user)
):
    """Join a group using join code"""
    try:
        group = await join_group(
            join_code=join_data.join_code,
            user_id=current_user["uid"]
        )
        
        if not group:
            raise HTTPException(
                status_code=404,
                detail="Group not found with this join code"
            )
        
        return MessageResponse(
            message=f"Successfully joined group: {group['name']}",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to join group: {str(e)}"
        )

@router.get("/my-groups")
async def get_my_groups(
    current_user = Depends(get_current_user)
):
    """Get all groups the user is a member of"""
    try:
        from database import get_db
        db = get_db()
        
        # Get user's group memberships
        memberships = db.collection("group_members").where("userId", "==", current_user["uid"]).stream()
        
        groups = []
        for membership in memberships:
            member_data = membership.to_dict()
            group_id = member_data["groupId"]
            
            # Get group details
            group_doc = db.collection("groups").document(group_id).get()
            if group_doc.exists:
                group_data = group_doc.to_dict()
                group_data["id"] = group_id
                
                # Count members
                member_count = len(list(db.collection("group_members").where("groupId", "==", group_id).stream()))
                group_data["member_count"] = member_count
                group_data["my_role"] = member_data["role"]
                
                groups.append(group_data)
        
        return {
            "groups": groups,
            "total_count": len(groups)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get groups: {str(e)}"
        )

@router.get("/{group_id}/leaderboard")
async def get_group_leaderboard(
    group_id: str,
    current_user = Depends(get_current_user)
):
    """Get leaderboard for a specific group"""
    try:
        from database import get_db
        from datetime import datetime, timedelta
        db = get_db()
        
        # Check if user is member of this group
        membership = db.collection("group_members").document(f"{group_id}_{current_user['uid']}").get()
        if not membership.exists:
            raise HTTPException(
                status_code=403,
                detail="You are not a member of this group"
            )
        
        # Get group info
        group_doc = db.collection("groups").document(group_id).get()
        if not group_doc.exists:
            raise HTTPException(
                status_code=404,
                detail="Group not found"
            )
        
        group_data = group_doc.to_dict()
        
        # Get all group members
        members = db.collection("group_members").where("groupId", "==", group_id).stream()
        
        leaderboard = []
        week_start = datetime.utcnow() - timedelta(days=7)
        
        for member in members:
            member_data = member.to_dict()
            user_id = member_data["userId"]
            
            # Get user info
            user_doc = db.collection("users").document(user_id).get()
            user_info = user_doc.to_dict() if user_doc.exists else {}
            
            # Calculate consistency score (logs in last 7 days)
            logs_count = len(list(
                db.collection("habit_logs")
                .where("uid", "==", user_id)
                .where("timestamp", ">=", week_start)
                .stream()
            ))
            
            # Simple consistency score: logs per day (max 7 days = 100%)
            consistency_score = min(100, (logs_count / 7) * 100)
            
            leaderboard.append({
                "user_id": user_id,
                "display_name": user_info.get("displayName", "Anonymous"),
                "role": member_data["role"],
                "consistency_score": round(consistency_score, 1),
                "weekly_logs": logs_count
            })
        
        # Sort by consistency score
        leaderboard.sort(key=lambda x: x["consistency_score"], reverse=True)
        
        return {
            "group_id": group_id,
            "group_name": group_data["name"],
            "leaderboard": leaderboard,
            "week_start": week_start,
            "total_members": len(leaderboard)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get leaderboard: {str(e)}"
        )
