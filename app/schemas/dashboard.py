from pydantic import BaseModel
from typing import List


class CategoryTotal(BaseModel):
    category: str
    total: float
    count: int


class MonthlyTrend(BaseModel):
    year: int
    month: int
    income: float
    expense: float
    net: float


class RecentTransaction(BaseModel):
    id: str
    amount: float
    type: str
    category: str
    date: str
    notes: str | None


class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    total_transactions: int
    income_by_category: List[CategoryTotal]
    expense_by_category: List[CategoryTotal]
    monthly_trends: List[MonthlyTrend]
    recent_transactions: List[RecentTransaction]
