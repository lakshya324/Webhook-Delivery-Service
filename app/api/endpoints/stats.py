from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import delivery as delivery_crud
from app.crud import subscription as subscription_crud
from app.schemas import DeliveryLog

router = APIRouter()

@router.get("/subscription/{subscription_id}")
def get_subscription_stats(subscription_id: str, db: Session = Depends(get_db)):
    """
    Get delivery statistics for a subscription
    """
    # Check if subscription exists
    subscription = subscription_crud.get_subscription(db, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Get stats
    stats = delivery_crud.get_delivery_stats_by_subscription(db, subscription_id)
    
    # Add subscription details
    stats["subscription_id"] = subscription_id
    stats["target_url"] = subscription.target_url
    
    return stats

@router.get("/recent-attempts/{subscription_id}", response_model=List[DeliveryLog])
def get_recent_attempts(
    subscription_id: str, limit: int = 20, db: Session = Depends(get_db)
):
    """
    Get recent delivery attempts for a subscription
    """
    # Check if subscription exists
    subscription = subscription_crud.get_subscription(db, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Here we'd typically get recent delivery attempts
    # For simplicity, we'll just get any logs for this subscription
    # In a real implementation, you'd want to join with the webhook table
    # and order by timestamp
    
    # Get recent logs
    logs = db.query(delivery_crud.DeliveryLog).filter(
        delivery_crud.DeliveryLog.subscription_id == subscription_id
    ).order_by(delivery_crud.DeliveryLog.attempt_timestamp.desc()).limit(limit).all()
    
    return logs