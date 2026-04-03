from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services import user_service
from app.middleware.auth import require_admin, require_any_role

router = APIRouter(prefix="/users", tags=["User Management"])


# @router.get("/me", response_model=UserResponse)
# async def get_me(current_user: dict = Depends(require_any_role)):
#     """Return the currently authenticated user's profile."""
#     return current_user

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(require_any_role)):
    """Return the currently authenticated user's profile."""
    return {
        "id": str(current_user["_id"]),  # 👈 FIX
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "status": current_user["status"],
        "created_at": current_user["created_at"],
    }

@router.get("/", response_model=List[UserResponse])
async def get_all_users(current_user: dict = Depends(require_admin)):
    """[Admin only] List all users."""
    return await user_service.list_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(require_admin)):
    """[Admin only] Get a specific user by ID."""
    return await user_service.get_user_by_id(user_id)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, current_user: dict = Depends(require_admin)):
    """[Admin only] Create a new user with any role."""
    return await user_service.create_user(data)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, data: UserUpdate, current_user: dict = Depends(require_admin)):
    """[Admin only] Update a user's name, email, role, or status."""
    return await user_service.update_user(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: str, current_user: dict = Depends(require_admin)):
    """[Admin only] Permanently delete a user."""
    return await user_service.delete_user(user_id)
