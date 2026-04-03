from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from app.models.enums import TransactionType, TransactionCategory


# ── Request Schemas ──────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    type: TransactionType
    category: TransactionCategory
    date: date
    notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator("notes", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    date: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator("notes", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        # Allow empty string — convert to None so backend stores null cleanly
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


# ── Filter Schema ────────────────────────────────────────────────────────────

class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    min_amount: Optional[float] = Field(default=None, gt=0)
    max_amount: Optional[float] = Field(default=None, gt=0)


# ── Response Schemas ─────────────────────────────────────────────────────────

class TransactionResponse(BaseModel):
    id: str
    amount: float
    type: TransactionType
    category: TransactionCategory
    date: date
    notes: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedTransactions(BaseModel):
    total: int
    page: int
    page_size: int
    data: list[TransactionResponse]
