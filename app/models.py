from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Enum as SQLAEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success" 
    FAILED_ATTEMPT = "failed_attempt"
    FAILURE = "failure"

class Subscription(Base):
    """
    Model for webhook subscriptions
    """
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    secret_key = Column(String, nullable=True)
    event_types = Column(JSON, nullable=True)  # For bonus: event type filtering
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with logs
    delivery_logs = relationship("DeliveryLog", back_populates="subscription")

class WebhookPayload(Base):
    """
    Model for storing incoming webhook payloads
    """
    __tablename__ = "webhook_payloads"

    id = Column(String, primary_key=True, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"))
    event_type = Column(String, nullable=True)  # For bonus: event type filtering
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with logs
    delivery_logs = relationship("DeliveryLog", back_populates="webhook_payload")

class DeliveryLog(Base):
    """
    Model for webhook delivery attempts and logs
    """
    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    webhook_id = Column(String, ForeignKey("webhook_payloads.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    attempt_number = Column(Integer, default=1)
    status = Column(SQLAEnum(DeliveryStatus), default=DeliveryStatus.PENDING)
    status_code = Column(Integer, nullable=True)
    error_details = Column(Text, nullable=True)
    attempt_timestamp = Column(DateTime, default=datetime.utcnow)
    next_attempt_at = Column(DateTime, nullable=True)
    
    # Relationships
    webhook_payload = relationship("WebhookPayload", back_populates="delivery_logs")
    subscription = relationship("Subscription", back_populates="delivery_logs")