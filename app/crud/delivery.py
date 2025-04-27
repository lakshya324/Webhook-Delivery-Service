from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import DeliveryLog, DeliveryStatus, WebhookPayload, Subscription
from app.schemas import DeliveryLogCreate
from app.core.config import settings

def create_delivery_log(db: Session, log: DeliveryLogCreate) -> DeliveryLog:
    """
    Create a new delivery log entry
    """
    db_log = DeliveryLog(
        webhook_id=log.webhook_id,
        subscription_id=log.subscription_id,
        attempt_number=log.attempt_number,
        status=log.status,
        status_code=log.status_code,
        error_details=log.error_details,
        next_attempt_at=log.next_attempt_at
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_delivery_logs(
    db: Session, webhook_id: str, skip: int = 0, limit: int = 100
) -> List[DeliveryLog]:
    """
    Get all delivery logs for a specific webhook
    """
    return (
        db.query(DeliveryLog)
        .filter(DeliveryLog.webhook_id == webhook_id)
        .order_by(DeliveryLog.attempt_number)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_latest_delivery_log(db: Session, webhook_id: str) -> Optional[DeliveryLog]:
    """
    Get the latest delivery log for a specific webhook
    """
    return (
        db.query(DeliveryLog)
        .filter(DeliveryLog.webhook_id == webhook_id)
        .order_by(DeliveryLog.attempt_number.desc())
        .first()
    )

def get_pending_deliveries(db: Session, limit: int = 100) -> List[Tuple[DeliveryLog, WebhookPayload, Subscription]]:
    """
    Get pending deliveries that are due for processing
    """
    now = datetime.utcnow()
    
    # Join with webhook_payloads and subscriptions to get all needed data in one query
    return (
        db.query(DeliveryLog, WebhookPayload, Subscription)
        .join(WebhookPayload, DeliveryLog.webhook_id == WebhookPayload.id)
        .join(Subscription, DeliveryLog.subscription_id == Subscription.id)
        .filter(
            DeliveryLog.status.in_([DeliveryStatus.PENDING, DeliveryStatus.FAILED_ATTEMPT]),
            DeliveryLog.next_attempt_at <= now,
            DeliveryLog.attempt_number <= settings.MAX_RETRY_ATTEMPTS
        )
        .order_by(DeliveryLog.next_attempt_at)
        .limit(limit)
        .all()
    )

def update_delivery_status(
    db: Session, 
    log_id: int, 
    status: DeliveryStatus, 
    status_code: Optional[int] = None, 
    error_details: Optional[str] = None,
    next_attempt_at: Optional[datetime] = None
) -> Optional[DeliveryLog]:
    """
    Update the status of a delivery log
    """
    db_log = db.query(DeliveryLog).filter(DeliveryLog.id == log_id).first()
    if not db_log:
        return None
    
    db_log.status = status
    if status_code is not None:
        db_log.status_code = status_code
    if error_details is not None:
        db_log.error_details = error_details
    if next_attempt_at is not None:
        db_log.next_attempt_at = next_attempt_at
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def create_next_attempt(db: Session, previous_log: DeliveryLog) -> DeliveryLog:
    """
    Create the next delivery attempt log based on previous attempt
    """
    attempt_number = previous_log.attempt_number + 1
    
    # Calculate next attempt time based on retry interval
    retry_delay = settings.RETRY_INTERVALS.get(
        attempt_number, settings.RETRY_INTERVALS[len(settings.RETRY_INTERVALS)]
    )
    next_attempt_at = datetime.utcnow() + timedelta(seconds=retry_delay)
    
    db_log = DeliveryLog(
        webhook_id=previous_log.webhook_id,
        subscription_id=previous_log.subscription_id,
        attempt_number=attempt_number,
        status=DeliveryStatus.PENDING,
        next_attempt_at=next_attempt_at
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def clean_old_logs(db: Session) -> int:
    """
    Delete logs older than the retention period
    Returns the number of logs deleted
    """
    retention_threshold = datetime.utcnow() - timedelta(hours=settings.LOG_RETENTION_HOURS)
    
    # Get count of logs to be deleted
    count_to_delete = db.query(func.count(DeliveryLog.id)).filter(
        DeliveryLog.attempt_timestamp < retention_threshold
    ).scalar()
    
    # Delete logs
    db.query(DeliveryLog).filter(
        DeliveryLog.attempt_timestamp < retention_threshold
    ).delete(synchronize_session=False)
    
    db.commit()
    return count_to_delete

def get_delivery_stats_by_subscription(db: Session, subscription_id: str) -> dict:
    """
    Get delivery statistics for a specific subscription
    """
    total_count = db.query(func.count(DeliveryLog.id)).filter(
        DeliveryLog.subscription_id == subscription_id
    ).scalar()
    
    success_count = db.query(func.count(DeliveryLog.id)).filter(
        DeliveryLog.subscription_id == subscription_id,
        DeliveryLog.status == DeliveryStatus.SUCCESS
    ).scalar()
    
    failure_count = db.query(func.count(DeliveryLog.id)).filter(
        DeliveryLog.subscription_id == subscription_id,
        DeliveryLog.status == DeliveryStatus.FAILURE
    ).scalar()
    
    pending_count = db.query(func.count(DeliveryLog.id)).filter(
        DeliveryLog.subscription_id == subscription_id,
        DeliveryLog.status.in_([DeliveryStatus.PENDING, DeliveryStatus.FAILED_ATTEMPT])
    ).scalar()
    
    return {
        "total": total_count,
        "success": success_count,
        "failure": failure_count,
        "pending": pending_count,
        "success_rate": (success_count / total_count * 100) if total_count > 0 else 0
    }