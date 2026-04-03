from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.enums import UserRole, UserStatus


# ── Request Schemas ──────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class LoginRequest(BaseModel):
    email: EmailStr
    # Cap at 72 chars at the schema level — bcrypt's hard limit is 72 bytes.
    # The security layer also pre-hashes with SHA-256 as a belt-and-suspenders fix.
    password: str = Field(..., min_length=1, max_length=72)


# ── Response Schemas ─────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    status: UserStatus
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
