from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Dict, Any
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import UserOut, MessageResponse
from crud import create_or_update_user
import firebase_admin
from firebase_admin import auth

router = APIRouter()

async def get_current_user(authorization: str = Header(None)) -> Dict[str, Any]:
    """Verify Firebase ID token and return user info"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Authorization header with Bearer token required"
        )
    
    # Extract token
    token = authorization.split(" ", 1)[1]
    
    try:
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )

@router.post("/verify", response_model=MessageResponse)
async def verify_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Verify user token and ensure user exists in database"""
    try:
        # Create or update user in Firestore
        user_data = await create_or_update_user(
            uid=current_user["uid"],
            email=current_user.get("email"),
            display_name=current_user.get("name"),
            photo_url=current_user.get("picture")
        )
        
        return MessageResponse(
            message="User verified successfully",
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify user: {str(e)}"
        )

@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return UserOut(
        uid=current_user["uid"],
        email=current_user.get("email"),
        displayName=current_user.get("name"),
        photoUrl=current_user.get("picture")
    )
