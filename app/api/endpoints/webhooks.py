import hashlib
import hmac
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import WebhookPayloadCreate, WebhookPayload, DeliveryLog, DeliveryStatus
from app.crud import webhook as webhook_crud
from app.crud import subscription as subscription_crud
from app.crud import delivery as delivery_crud

router = APIRouter()


@router.post("/ingest/{subscription_id}", status_code=status.HTTP_202_ACCEPTED)
async def ingest_webhook(
    subscription_id: str,
    request: Request,
    x_webhook_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Ingest a webhook for a subscription
    
    This endpoint accepts a webhook payload and queues it for delivery to the subscription target URL.
    """
    # Check if subscription exists
    subscription = subscription_crud.get_subscription(db, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Parse the request body
    payload = await request.json()
    
    # Event type filtering (bonus feature)
    if subscription.event_types and x_webhook_event:
        if x_webhook_event not in subscription.event_types:
            # Skip this webhook as the subscription doesn't listen for this event
            return {
                "status": "skipped", 
                "message": f"Subscription {subscription_id} does not listen for event {x_webhook_event}"
            }
    
    # Signature verification (bonus feature)
    if subscription.secret_key and x_hub_signature_256:
        # Verify the signature
        body = await request.body()
        expected_signature = hmac.new(
            subscription.secret_key.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Remove "sha256=" prefix if present
        received_signature = x_hub_signature_256
        if received_signature.startswith("sha256="):
            received_signature = received_signature[7:]
        
        if not hmac.compare_digest(expected_signature, received_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Create webhook payload
    webhook_payload = WebhookPayloadCreate(
        subscription_id=subscription_id,
        payload=payload,
        event_type=x_webhook_event
    )
    
    # Save and queue for delivery
    db_webhook = webhook_crud.create_webhook_payload(db, webhook_payload)
    
    return {
        "status": "accepted", 
        "webhook_id": db_webhook.id, 
        "message": "Webhook accepted and queued for delivery"
    }


@router.get("/{webhook_id}/status", response_model=List[DeliveryLog])
def get_webhook_status(webhook_id: str, db: Session = Depends(get_db)):
    """
    Get the delivery status of a webhook
    """
    # Check if webhook exists
    webhook = webhook_crud.get_webhook_payload(db, webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Get all delivery attempts
    delivery_logs = delivery_crud.get_delivery_logs(db, webhook_id)
    
    return delivery_logs


@router.get("/subscription/{subscription_id}", response_model=List[WebhookPayload])
def get_subscription_webhooks(
    subscription_id: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    """
    Get all webhooks for a subscription
    """
    # Check if subscription exists
    subscription = subscription_crud.get_subscription(db, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Get webhooks
    webhooks = webhook_crud.get_webhooks_by_subscription(
        db, subscription_id, skip=skip, limit=limit
    )
    
    return webhooks