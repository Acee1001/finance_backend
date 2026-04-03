from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from app.core.database import get_database
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, UserUpdate, LoginRequest
from app.models.enums import UserStatus


def _serialize_user(user: dict) -> dict:
    """Convert MongoDB document to a JSON-serializable dict."""
    user["id"] = str(user["_id"])
    del user["_id"]
    user.pop("password", None)
    return user


async def create_user(data: UserCreate) -> dict:
    db = get_database()

    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user_doc = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "role": data.role.value,
        "status": UserStatus.ACTIVE.value,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return _serialize_user(user_doc)


async def login_user(data: LoginRequest) -> dict:
    db = get_database()
    user = await db.users.find_one({"email": data.email})

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if user.get("status") == UserStatus.INACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact an administrator.",
        )

    token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
    serialized = _serialize_user(dict(user))
    return {"access_token": token, "token_type": "bearer", "user": serialized}


async def list_users() -> list:
    db = get_database()
    users = await db.users.find({}, {"password": 0}).to_list(length=1000)
    for u in users:
        u["id"] = str(u["_id"])
        del u["_id"]
    return users


async def get_user_by_id(user_id: str) -> dict:
    db = get_database()
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user["id"] = str(user["_id"])
    del user["_id"]
    return user


async def update_user(user_id: str, data: UserUpdate) -> dict:
    db = get_database()
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    update_fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    # Store enum values as strings
    for key in ("role", "status"):
        if key in update_fields and hasattr(update_fields[key], "value"):
            update_fields[key] = update_fields[key].value

    update_fields["updated_at"] = datetime.utcnow()

    result = await db.users.find_one_and_update(
        {"_id": oid},
        {"$set": update_fields},
        projection={"password": 0},
        return_document=True,
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result["id"] = str(result["_id"])
    del result["_id"]
    return result


async def delete_user(user_id: str) -> dict:
    db = get_database()
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")

    result = await db.users.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "User deleted successfully"}
