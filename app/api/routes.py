from fastapi import APIRouter
from app.api.endpoints import subscriptions, webhooks, stats

api_router = APIRouter()

# Include the different routes
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])