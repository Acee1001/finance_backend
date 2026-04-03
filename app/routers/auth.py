from fastapi import APIRouter, status
from app.schemas.user import UserCreate, LoginRequest, TokenResponse, UserResponse
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):
    """
    Register a new user.
    - Anyone can register; default role is **viewer**.
    - Only an admin can create analyst/admin accounts via the users endpoint.
    """
    user = await user_service.create_user(data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """Authenticate and receive a JWT access token."""
    return await user_service.login_user(data)
