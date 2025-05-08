from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import Subscription, SubscriptionCreate, SubscriptionUpdate
from app.crud import subscription as subscription_crud

router = APIRouter()

@router.post("/", response_model=Subscription, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription: SubscriptionCreate, db: Session = Depends(get_db)
):
    """
    Create a new webhook subscription
    """
    db_subscription = subscription_crud.create_subscription(db, subscription)
    return db_subscription

@router.get("/", response_model=List[Subscription])
def read_subscriptions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve all webhook subscriptions
    """
    subscriptions = subscription_crud.get_subscriptions(db, skip=skip, limit=limit)
    return subscriptions

@router.get("/{subscription_id}", response_model=Subscription)
def read_subscription(
    subscription_id: str, db: Session = Depends(get_db)
):
    """
    Retrieve a specific webhook subscription by ID
    """
    db_subscription = subscription_crud.get_subscription(db, subscription_id)
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return db_subscription

@router.put("/{subscription_id}", response_model=Subscription)
def update_subscription(
    subscription_id: str, subscription: SubscriptionUpdate, db: Session = Depends(get_db)
):
    """
    Update a webhook subscription
    """
    db_subscription = subscription_crud.update_subscription(
        db, subscription_id, subscription
    )
    if db_subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return db_subscription

@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: str, db: Session = Depends(get_db)
):
    """
    Delete a webhook subscription
    """
    success = subscription_crud.delete_subscription(db, subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return None