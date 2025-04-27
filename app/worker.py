import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.crud import delivery as delivery_crud
from app.models import DeliveryLog, WebhookPayload, Subscription
from app.services.delivery_service import WebhookDeliveryService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookWorker:
    def __init__(self, batch_size: int = 20, polling_interval: int = 5):
        """
        Initialize the webhook worker
        
        Args:
            batch_size: Number of webhooks to process in a single batch
            polling_interval: How often to check for new webhooks (in seconds)
        """
        self.batch_size = batch_size
        self.polling_interval = polling_interval
        self.running = False
    
    async def process_webhook_batch(self, db: Session) -> int:
        """
        Process a batch of pending webhook deliveries
        
        Returns the number of webhooks processed
        """
        # Get pending deliveries
        pending_deliveries = delivery_crud.get_pending_deliveries(
            db, limit=self.batch_size
        )
        
        if not pending_deliveries:
            return 0
            
        logger.info(f"Processing {len(pending_deliveries)} pending webhook deliveries")
        
        # Process each delivery
        tasks = []
        for delivery_log, webhook_payload, subscription in pending_deliveries:
            task = self._process_single_delivery(
                db=db,
                log=delivery_log,
                webhook_payload=webhook_payload,
                subscription=subscription
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        return len(pending_deliveries)
    
    async def _process_single_delivery(
        self, db: Session, log: DeliveryLog, webhook_payload: WebhookPayload, subscription: Subscription
    ) -> None:
        """Process a single webhook delivery"""
        logger.info(
            f"Processing webhook {webhook_payload.id} to {subscription.target_url} "
            f"(Attempt #{log.attempt_number})"
        )
        
        # Process the delivery
        success, status_code, error_details = await WebhookDeliveryService.process_delivery(
            db=db,
            log=log,
            webhook_payload=webhook_payload.payload,
            target_url=subscription.target_url,
            secret_key=subscription.secret_key,
            event_type=webhook_payload.event_type
        )
        
        # Handle result
        updated_log, should_retry = await WebhookDeliveryService.handle_delivery_result(
            db=db,
            log=log,
            success=success,
            status_code=status_code,
            error_details=error_details
        )
        
        if success:
            logger.info(f"Webhook {webhook_payload.id} delivered successfully")
        elif should_retry:
            logger.info(
                f"Webhook {webhook_payload.id} delivery failed, "
                f"will retry (attempt {log.attempt_number + 1}) at {updated_log.next_attempt_at}"
            )
        else:
            logger.warning(f"Webhook {webhook_payload.id} delivery failed permanently: {error_details}")
    
    async def cleanup_old_logs(self) -> None:
        """Clean up old logs based on retention policy"""
        try:
            db = SessionLocal()
            count = delivery_crud.clean_old_logs(db)
            if count > 0:
                logger.info(f"Cleaned up {count} old delivery logs")
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
        finally:
            db.close()
    
    async def run(self) -> None:
        """Run the webhook worker in an infinite loop"""
        self.running = True
        
        try:
            while self.running:
                db = SessionLocal()
                try:
                    # Process webhooks
                    processed_count = await self.process_webhook_batch(db)
                    
                    # If we didn't process any webhooks, wait before trying again
                    if processed_count == 0:
                        await asyncio.sleep(self.polling_interval)
                        
                    # Occasionally clean up old logs (once per hour)
                    if datetime.utcnow().minute == 0:  # at the start of each hour
                        await self.cleanup_old_logs()
                        
                except Exception as e:
                    logger.error(f"Error processing webhook batch: {e}")
                    await asyncio.sleep(self.polling_interval)
                finally:
                    db.close()
        except asyncio.CancelledError:
            self.running = False
            logger.info("Webhook worker shutdown")
    
    def stop(self) -> None:
        """Stop the webhook worker"""
        self.running = False

# Function to start the worker in the background
async def start_webhook_worker() -> WebhookWorker:
    worker = WebhookWorker()
    asyncio.create_task(worker.run())
    logger.info("Webhook worker started")
    return worker

# For running the worker standalone (for testing)
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    worker = WebhookWorker()
    try:
        loop.run_until_complete(worker.run())
    except KeyboardInterrupt:
        worker.stop()
        logger.info("Worker stopped by user")