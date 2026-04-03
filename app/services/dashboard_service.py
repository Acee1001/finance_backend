from app.core.database import get_database


async def get_dashboard_summary() -> dict:
    db = get_database()

    # ── 1. Total income and expense ──────────────────────────────────────────
    totals_pipeline = [
        {
            "$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
            }
        }
    ]
    totals_result = await db.transactions.aggregate(totals_pipeline).to_list(length=10)

    total_income = 0.0
    total_expense = 0.0
    total_transactions = 0

    for item in totals_result:
        if item["_id"] == "income":
            total_income = item["total"]
        elif item["_id"] == "expense":
            total_expense = item["total"]
        total_transactions += item["count"]

    net_balance = total_income - total_expense

    # ── 2. Category-wise totals ──────────────────────────────────────────────
    category_pipeline = [
        {
            "$group": {
                "_id": {"type": "$type", "category": "$category"},
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"total": -1}},
    ]
    category_result = await db.transactions.aggregate(category_pipeline).to_list(length=100)

    income_by_category = []
    expense_by_category = []

    for item in category_result:
        entry = {
            "category": item["_id"]["category"],
            "total": item["total"],
            "count": item["count"],
        }
        if item["_id"]["type"] == "income":
            income_by_category.append(entry)
        else:
            expense_by_category.append(entry)

    # ── 3. Monthly trends (last 6 months) ───────────────────────────────────
    monthly_pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"},
                    "type": "$type",
                },
                "total": {"$sum": "$amount"},
            }
        },
        {"$sort": {"_id.year": -1, "_id.month": -1}},
        {"$limit": 24},
    ]
    monthly_result = await db.transactions.aggregate(monthly_pipeline).to_list(length=100)

    # Merge income/expense into monthly buckets
    monthly_map: dict = {}
    for item in monthly_result:
        key = (item["_id"]["year"], item["_id"]["month"])
        if key not in monthly_map:
            monthly_map[key] = {"year": key[0], "month": key[1], "income": 0.0, "expense": 0.0}
        monthly_map[key][item["_id"]["type"]] += item["total"]

    monthly_trends = [
        {**v, "net": v["income"] - v["expense"]}
        for v in sorted(monthly_map.values(), key=lambda x: (x["year"], x["month"]), reverse=True)
    ][:6]

    # ── 4. Recent transactions ───────────────────────────────────────────────
    recent_cursor = db.transactions.find().sort("created_at", -1).limit(10)
    recent_raw = await recent_cursor.to_list(length=10)

    recent_transactions = [
        {
            "id": str(t["_id"]),
            "amount": t["amount"],
            "type": t["type"],
            "category": t["category"],
            "date": t["date"].strftime("%Y-%m-%d") if hasattr(t["date"], "strftime") else str(t["date"]),
            "notes": t.get("notes"),
        }
        for t in recent_raw
    ]

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "net_balance": round(net_balance, 2),
        "total_transactions": total_transactions,
        "income_by_category": income_by_category,
        "expense_by_category": expense_by_category,
        "monthly_trends": monthly_trends,
        "recent_transactions": recent_transactions,
    }
