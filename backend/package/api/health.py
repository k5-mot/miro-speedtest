from fastapi import APIRouter
from pydantic import BaseModel

from package.common import get_logger, get_settings

settings = get_settings()
logger = get_logger()
router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    message: str


# app.include_router(users.router, tags=["Health"], prefix="/api/health")


@router.get("/status")
def health_status() -> HealthResponse:
    """ユーザーセッションの状態を取得."""
    return HealthResponse(status="Healthy", message="Service is running")
