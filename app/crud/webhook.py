import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import WebhookPayload, DeliveryLog, DeliveryStatus
from app.schemas import WebhookPayloadCreate

def create_webhook_payload(db: Session, webhook: WebhookPayloadCreate) -> WebhookPayload:
    """
    Create a new webhook payload entry
    """
    if not webhook.payload:
        raise ValueError("Webhook payload cannot be empty")
        
    webhook_id = str(uuid.uuid4())
    db_webhook = WebhookPayload(
        id=webhook_id,
        subscription_id=webhook.subscription_id,
        event_type=webhook.event_type,
        payload=webhook.payload
    )
    db.add(db_webhook)
    
    # Create initial delivery log entry
    initial_log = DeliveryLog(
        webhook_id=webhook_id,
        subscription_id=webhook.subscription_id,
        attempt_number=1,
        status=DeliveryStatus.PENDING,
        next_attempt_at=datetime.utcnow()  # Ready for immediate processing
    )
    db.add(initial_log)
    
    db.commit()
    db.refresh(db_webhook)
    return db_webhook

def get_webhook_payload(db: Session, webhook_id: str) -> Optional[WebhookPayload]:
    """
    Get a webhook payload by ID
    """
    return db.query(WebhookPayload).filter(WebhookPayload.id == webhook_id).first()

def get_webhooks_by_subscription(
    db: Session, subscription_id: str, skip: int = 0, limit: int = 100
) -> List[WebhookPayload]:
    """
    Get all webhook payloads for a specific subscription
    """
    return (
        db.query(WebhookPayload)
        .filter(WebhookPayload.subscription_id == subscription_id)
        .order_by(WebhookPayload.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )