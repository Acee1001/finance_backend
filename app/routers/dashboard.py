from fastapi import APIRouter, Depends
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard_service
from app.middleware.auth import require_analyst_or_above

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(current_user: dict = Depends(require_analyst_or_above)):
    """
    [Analyst & Admin] Full dashboard summary including:
    - Total income, expenses, net balance
    - Category-wise breakdowns
    - Monthly trends (last 6 months)
    - 10 most recent transactions
    """
    return await dashboard_service.get_dashboard_summary()
