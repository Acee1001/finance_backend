from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from datetime import date
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionFilter,
    TransactionResponse,
    PaginatedTransactions,
)
from app.services import transaction_service
from app.middleware.auth import require_admin, require_analyst_or_above, require_any_role
from app.models.enums import TransactionType, TransactionCategory

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=PaginatedTransactions)
async def list_transactions(
    type: Optional[TransactionType] = Query(None, description="Filter by income or expense"),
    category: Optional[TransactionCategory] = Query(None, description="Filter by category"),
    date_from: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    min_amount: Optional[float] = Query(None, gt=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, gt=0, description="Maximum amount"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page"),
    current_user: dict = Depends(require_any_role),
):
    """
    [All roles] List transactions with optional filters and pagination.
    - type, category, date_from, date_to, min_amount, max_amount
    """
    filters = TransactionFilter(
        type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
    )
    return await transaction_service.list_transactions(filters, page, page_size)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, current_user: dict = Depends(require_any_role)):
    """[All roles] Get a single transaction by ID."""
    return await transaction_service.get_transaction_by_id(transaction_id)


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    current_user: dict = Depends(require_admin),
):
    """[Admin only] Create a new financial transaction."""
    return await transaction_service.create_transaction(data, current_user)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    data: TransactionUpdate,
    current_user: dict = Depends(require_admin),
):
    """[Admin only] Update an existing transaction."""
    return await transaction_service.update_transaction(transaction_id, data)


@router.delete("/{transaction_id}", status_code=status.HTTP_200_OK)
async def delete_transaction(
    transaction_id: str,
    current_user: dict = Depends(require_admin),
):
    """[Admin only] Delete a transaction."""
    return await transaction_service.delete_transaction(transaction_id)
