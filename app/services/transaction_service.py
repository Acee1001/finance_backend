from datetime import datetime, date
from bson import ObjectId
from fastapi import HTTPException, status
from app.core.database import get_database
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionFilter


# ─────────────────────────────────────────────────────────────
# Helper: Serialize MongoDB document → API response
# ─────────────────────────────────────────────────────────────
def _serialize_transaction(t: dict) -> dict:
    return {
        "id": str(t["_id"]),
        "amount": t["amount"],
        "type": t["type"],
        "category": t["category"],
        "date": t["date"].date() if isinstance(t.get("date"), datetime) else t.get("date"),
        "notes": t.get("notes"),
        "created_by": str(t.get("created_by_id")) if t.get("created_by_id") else None,
        "created_at": t.get("created_at"),
        "updated_at": t.get("updated_at"),
    }


def _date_to_datetime(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time())


# ─────────────────────────────────────────────────────────────
# CREATE TRANSACTION
# ─────────────────────────────────────────────────────────────
async def create_transaction(data: TransactionCreate, current_user: dict) -> dict:
    db = get_database()

    user_id = current_user.get("id") or current_user.get("sub") or current_user.get("_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in token"
        )

    doc = {
        "amount": data.amount,
        "type": data.type.value,
        "category": data.category.value,
        "date": _date_to_datetime(data.date),
        "notes": data.notes,
        "created_by_id": ObjectId(user_id),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.transactions.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "amount": doc["amount"],
        "type": doc["type"],
        "category": doc["category"],
        "date": data.date,
        "notes": doc["notes"],
        "created_by": str(user_id),
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
    }


# ─────────────────────────────────────────────────────────────
# LIST TRANSACTIONS
# ─────────────────────────────────────────────────────────────
async def list_transactions(filters: TransactionFilter, page: int, page_size: int) -> dict:
    db = get_database()
    query = {}

    if filters.type:
        query["type"] = filters.type.value

    if filters.category:
        query["category"] = filters.category.value

    if filters.date_from or filters.date_to:
        date_query = {}
        if filters.date_from:
            date_query["$gte"] = _date_to_datetime(filters.date_from)
        if filters.date_to:
            date_query["$lte"] = _date_to_datetime(filters.date_to)
        query["date"] = date_query

    if filters.min_amount or filters.max_amount:
        amount_query = {}
        if filters.min_amount:
            amount_query["$gte"] = filters.min_amount
        if filters.max_amount:
            amount_query["$lte"] = filters.max_amount
        query["amount"] = amount_query

    total = await db.transactions.count_documents(query)
    skip = (page - 1) * page_size

    cursor = (
        db.transactions
        .find(query)
        .sort("date", -1)
        .skip(skip)
        .limit(page_size)
    )

    transactions = await cursor.to_list(length=page_size)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [_serialize_transaction(t) for t in transactions],
    }


# ─────────────────────────────────────────────────────────────
# GET TRANSACTION BY ID
# ─────────────────────────────────────────────────────────────
async def get_transaction_by_id(transaction_id: str) -> dict:
    db = get_database()

    try:
        oid = ObjectId(transaction_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID"
        )

    t = await db.transactions.find_one({"_id": oid})

    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return _serialize_transaction(t)


# ─────────────────────────────────────────────────────────────
# UPDATE TRANSACTION  ← BUG FIX HERE
# ─────────────────────────────────────────────────────────────
async def update_transaction(transaction_id: str, data: TransactionUpdate) -> dict:
    db = get_database()

    try:
        oid = ObjectId(transaction_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID"
        )

    # ✅ FIX: use exclude_unset=True so only fields the client actually sent
    #         are included — this avoids Pydantic v2 "Input should be None"
    #         errors caused by Optional fields being coerced incorrectly.
    update_fields = data.model_dump(exclude_unset=True)

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    # Convert enums → string values
    if "type" in update_fields and hasattr(update_fields["type"], "value"):
        update_fields["type"] = update_fields["type"].value

    if "category" in update_fields and hasattr(update_fields["category"], "value"):
        update_fields["category"] = update_fields["category"].value

    # Convert date → datetime for MongoDB storage
    if "date" in update_fields and update_fields["date"] is not None:
        update_fields["date"] = _date_to_datetime(update_fields["date"])

    # ✅ FIX: handle notes="" — validator already converts to None,
    #         but also ensure "notes" key is kept so it can be cleared
    if "notes" in update_fields and update_fields["notes"] is None:
        pass  # Intentionally keep — allows clearing notes to null

    update_fields["updated_at"] = datetime.utcnow()

    updated = await db.transactions.find_one_and_update(
        {"_id": oid},
        {"$set": update_fields},
        return_document=True
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return _serialize_transaction(updated)


# ─────────────────────────────────────────────────────────────
# DELETE TRANSACTION
# ─────────────────────────────────────────────────────────────
async def delete_transaction(transaction_id: str) -> dict:
    db = get_database()

    try:
        oid = ObjectId(transaction_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID"
        )

    result = await db.transactions.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return {"message": "Transaction deleted successfully"}
