# """
# Seed script — run once to populate the database with:
#   - 1 admin user
#   - 1 analyst user
#   - 1 viewer user
#   - 15 sample transactions

# Usage:
#     python seed.py
# """

# import asyncio
# from datetime import datetime, date, timedelta
# import random
# import os
# from dotenv import load_dotenv
# from motor.motor_asyncio import AsyncIOMotorClient
# from passlib.context import CryptContext

# # Load environment variables
# load_dotenv()

# # Get values from .env
# MONGODB_URL = os.getenv("MONGODB_URL")
# DATABASE_NAME = os.getenv("DATABASE_NAME")

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# USERS = [
#     {"name": "Alice Admin", "email": "admin@finance.dev", "password": "admin123", "role": "admin"},
#     {"name": "Ana Analyst", "email": "analyst@finance.dev", "password": "analyst123", "role": "analyst"},
#     {"name": "Victor Viewer", "email": "viewer@finance.dev", "password": "viewer123", "role": "viewer"},
# ]

# SAMPLE_TRANSACTIONS = [
#     {"amount": 85000, "type": "income", "category": "salary", "notes": "Monthly salary"},
#     {"amount": 12000, "type": "income", "category": "freelance", "notes": "Freelance project"},
#     {"amount": 5000, "type": "income", "category": "investment", "notes": "Dividend income"},
#     {"amount": 22000, "type": "expense", "category": "rent", "notes": "Monthly rent"},
#     {"amount": 4500, "type": "expense", "category": "food", "notes": "Groceries and dining"},
#     {"amount": 1800, "type": "expense", "category": "transport", "notes": "Fuel and auto"},
#     {"amount": 2200, "type": "expense", "category": "utilities", "notes": "Electricity and internet"},
#     {"amount": 3500, "type": "expense", "category": "entertainment", "notes": "Streaming + outings"},
#     {"amount": 1500, "type": "expense", "category": "healthcare", "notes": "Clinic visit"},
#     {"amount": 90000, "type": "income", "category": "salary", "notes": "Monthly salary"},
#     {"amount": 8000, "type": "income", "category": "freelance", "notes": "Design gig"},
#     {"amount": 22000, "type": "expense", "category": "rent", "notes": "Monthly rent"},
#     {"amount": 5200, "type": "expense", "category": "food", "notes": "Groceries"},
#     {"amount": 900, "type": "expense", "category": "transport", "notes": "Cab expenses"},
#     {"amount": 3000, "type": "expense", "category": "entertainment", "notes": "Weekend trip"},
# ]


# async def seed():
#     if not MONGODB_URL:
#         raise ValueError("❌ MONGODB_URL not found in .env")

#     print("Mongo URL:", MONGODB_URL)

#     client = AsyncIOMotorClient(MONGODB_URL)
#     db = client[DATABASE_NAME]

#     print("🌱  Seeding database...")

#     # Clear existing data
#     await db.users.delete_many({})
#     await db.transactions.delete_many({})
#     print("   Cleared existing data.")

#     # Insert users
#     now = datetime.utcnow()
#     inserted_users = []

#     for u in USERS:
#         doc = {
#             "name": u["name"],
#             "email": u["email"],
#             "password": pwd_context.hash(u["password"]),
#             "role": u["role"],
#             "status": "active",
#             "created_at": now,
#             "updated_at": now,
#         }
#         result = await db.users.insert_one(doc)
#         inserted_users.append(result.inserted_id)
#         print(f"   ✅ Created {u['role']}: {u['email']} / {u['password']}")

#     admin_id = inserted_users[0]

#     # Insert transactions
#     today = date.today()

#     for t in SAMPLE_TRANSACTIONS:
#         days_ago = random.randint(0, 90)
#         tx_date = today - timedelta(days=days_ago)

#         doc = {
#             "amount": t["amount"],
#             "type": t["type"],
#             "category": t["category"],
#             "notes": t["notes"],
#             "date": datetime.combine(tx_date, datetime.min.time()),
#             "created_by_id": admin_id,
#             "created_at": now - timedelta(days=days_ago),
#             "updated_at": now - timedelta(days=days_ago),
#         }

#         await db.transactions.insert_one(doc)

#     print(f"   ✅ Inserted {len(SAMPLE_TRANSACTIONS)} sample transactions.")
#     print("\n🎉 Seeding complete! You can now start the server and log in.")

#     client.close()


# if __name__ == "__main__":
#     asyncio.run(seed())

"""
Seed script — run once to populate the database with:
  - 1 admin user
  - 1 analyst user
  - 1 viewer user
  - 15 sample transactions

Usage:
    python seed.py
"""

import asyncio
from datetime import datetime, date, timedelta
import random
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# Load environment variables
load_dotenv()

# Get values from .env
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS = [
    {"name": "Alice Admin", "email": "admin@finance.dev", "password": "admin123", "role": "admin"},
    {"name": "Ana Analyst", "email": "analyst@finance.dev", "password": "analyst123", "role": "analyst"},
    {"name": "Victor Viewer", "email": "viewer@finance.dev", "password": "viewer123", "role": "viewer"},
]

SAMPLE_TRANSACTIONS = [
    {"amount": 85000, "type": "income", "category": "salary", "notes": "Monthly salary"},
    {"amount": 12000, "type": "income", "category": "freelance", "notes": "Freelance project"},
    {"amount": 5000, "type": "income", "category": "investment", "notes": "Dividend income"},
    {"amount": 22000, "type": "expense", "category": "rent", "notes": "Monthly rent"},
    {"amount": 4500, "type": "expense", "category": "food", "notes": "Groceries and dining"},
    {"amount": 1800, "type": "expense", "category": "transport", "notes": "Fuel and auto"},
    {"amount": 2200, "type": "expense", "category": "utilities", "notes": "Electricity and internet"},
    {"amount": 3500, "type": "expense", "category": "entertainment", "notes": "Streaming + outings"},
    {"amount": 1500, "type": "expense", "category": "healthcare", "notes": "Clinic visit"},
    {"amount": 90000, "type": "income", "category": "salary", "notes": "Monthly salary"},
    {"amount": 8000, "type": "income", "category": "freelance", "notes": "Design gig"},
    {"amount": 22000, "type": "expense", "category": "rent", "notes": "Monthly rent"},
    {"amount": 5200, "type": "expense", "category": "food", "notes": "Groceries"},
    {"amount": 900, "type": "expense", "category": "transport", "notes": "Cab expenses"},
    {"amount": 3000, "type": "expense", "category": "entertainment", "notes": "Weekend trip"},
]


async def seed():
    if not MONGODB_URL:
        raise ValueError("❌ MONGODB_URL not found in .env")

    print("Mongo URL:", MONGODB_URL)

    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    print("🌱  Seeding database...")

    # Clear existing data
    await db.users.delete_many({})
    await db.transactions.delete_many({})
    print("   Cleared existing data.")

    # Insert users
    now = datetime.utcnow()
    inserted_users = []

    for u in USERS:
        doc = {
            "name": u["name"],
            "email": u["email"],
            "password": pwd_context.hash(u["password"]),
            "role": u["role"],
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }
        result = await db.users.insert_one(doc)
        inserted_users.append(result.inserted_id)
        print(f"   ✅ Created {u['role']}: {u['email']} / {u['password']}")

    admin_id = inserted_users[0]

    # Insert transactions
    today = date.today()

    for t in SAMPLE_TRANSACTIONS:
        days_ago = random.randint(0, 90)
        tx_date = today - timedelta(days=days_ago)

        doc = {
            "amount": t["amount"],
            "type": t["type"],
            "category": t["category"],
            "notes": t["notes"],
            "date": datetime.combine(tx_date, datetime.min.time()),
            "created_by_id": admin_id,
            "created_at": now - timedelta(days=days_ago),
            "updated_at": now - timedelta(days=days_ago),
        }

        await db.transactions.insert_one(doc)

    print(f"   ✅ Inserted {len(SAMPLE_TRANSACTIONS)} sample transactions.")
    print("\n🎉 Seeding complete! You can now start the server and log in.")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())