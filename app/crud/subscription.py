import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models import Subscription
from app.schemas import SubscriptionCreate, SubscriptionUpdate
from app.core.cache import RedisCache

def create_subscription(db: Session, subscription: SubscriptionCreate) -> Subscription:
    """
    Create a new subscription
    """
    db_subscription = Subscription(
        id=str(uuid.uuid4()),
        target_url=str(subscription.target_url),
        secret_key=subscription.secret_key,
        event_types=subscription.event_types,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    # Cache the subscription
    subscription_data = {
        "id": db_subscription.id,
        "target_url": db_subscription.target_url,
        "secret_key": db_subscription.secret_key,
        "event_types": db_subscription.event_types
    }
    RedisCache.set_subscription(db_subscription.id, subscription_data)
    
    return db_subscription

def get_subscription(db: Session, subscription_id: str) -> Optional[Subscription]:
    """
    Get a subscription by ID, using cache if available
    """
    # Try to get from cache first
    cached_subscription = RedisCache.get_subscription(subscription_id)
    if cached_subscription:
        # Convert cached data back to model
        return Subscription(
            id=cached_subscription["id"],
            target_url=cached_subscription["target_url"],
            secret_key=cached_subscription["secret_key"],
            event_types=cached_subscription["event_types"]
        )
    
    # If not in cache, get from database and cache it
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if db_subscription:
        subscription_data = {
            "id": db_subscription.id,
            "target_url": db_subscription.target_url,
            "secret_key": db_subscription.secret_key,
            "event_types": db_subscription.event_types
        }
        RedisCache.set_subscription(db_subscription.id, subscription_data)
    
    return db_subscription

def get_subscriptions(db: Session, skip: int = 0, limit: int = 100) -> List[Subscription]:
    """
    Get all subscriptions with pagination
    """
    return db.query(Subscription).offset(skip).limit(limit).all()

def update_subscription(
    db: Session, subscription_id: str, subscription_update: SubscriptionUpdate
) -> Optional[Subscription]:
    """
    Update a subscription
    """
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        return None
    
    update_data = subscription_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "target_url" and value:
            # Convert HttpUrl to string for storage
            setattr(db_subscription, key, str(value))
        else:
            setattr(db_subscription, key, value)
    
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    # Update cache
    subscription_data = {
        "id": db_subscription.id,
        "target_url": db_subscription.target_url,
        "secret_key": db_subscription.secret_key,
        "event_types": db_subscription.event_types
    }
    RedisCache.set_subscription(db_subscription.id, subscription_data)
    
    return db_subscription

def delete_subscription(db: Session, subscription_id: str) -> bool:
    """
    Delete a subscription
    """
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        return False
    
    # Delete from database
    db.delete(db_subscription)
    db.commit()
    
    # Delete from cache
    RedisCache.delete_subscription(subscription_id)
    
    return True