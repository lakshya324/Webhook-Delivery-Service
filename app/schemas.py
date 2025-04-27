from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, HttpUrl, Field

class DeliveryStatusEnum(str, Enum):
    PENDING = "pending"
    SUCCESS = "success" 
    FAILED_ATTEMPT = "failed_attempt"
    FAILURE = "failure"

# Subscription Schemas
class SubscriptionBase(BaseModel):
    target_url: HttpUrl
    secret_key: Optional[str] = None
    event_types: Optional[List[str]] = None  # For bonus: event type filtering

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    target_url: Optional[HttpUrl] = None
    secret_key: Optional[str] = None
    event_types: Optional[List[str]] = None

class SubscriptionInDB(SubscriptionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Subscription(SubscriptionInDB):
    pass

# Webhook Payload Schemas
class WebhookPayloadBase(BaseModel):
    payload: Dict[str, Any]
    event_type: Optional[str] = None  # For bonus: event type filtering

class WebhookPayloadCreate(WebhookPayloadBase):
    subscription_id: str

class WebhookPayloadInDB(WebhookPayloadBase):
    id: str
    subscription_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class WebhookPayload(WebhookPayloadInDB):
    pass

# Delivery Log Schemas
class DeliveryLogBase(BaseModel):
    webhook_id: str
    subscription_id: str
    attempt_number: int
    status: DeliveryStatusEnum
    status_code: Optional[int] = None
    error_details: Optional[str] = None
    attempt_timestamp: datetime
    next_attempt_at: Optional[datetime] = None

class DeliveryLogCreate(BaseModel):
    webhook_id: str
    subscription_id: str
    attempt_number: int = 1
    status: DeliveryStatusEnum = DeliveryStatusEnum.PENDING
    status_code: Optional[int] = None
    error_details: Optional[str] = None
    next_attempt_at: Optional[datetime] = None

class DeliveryLogInDB(DeliveryLogBase):
    id: int

    class Config:
        from_attributes = True

class DeliveryLog(DeliveryLogInDB):
    pass

class DeliveryStatus(BaseModel):
    webhook_id: str
    subscription_id: str
    target_url: HttpUrl
    current_status: DeliveryStatusEnum
    attempt_count: int
    last_attempt: datetime
    next_attempt: Optional[datetime] = None
    history: List[DeliveryLog] = []