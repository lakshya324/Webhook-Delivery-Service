import asyncio
import hmac
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any

import aiohttp
from sqlalchemy.orm import Session

from app.models import DeliveryStatus, DeliveryLog
from app.crud import delivery as delivery_crud
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookDeliveryService:
    @staticmethod
    async def process_delivery(
        db: Session, 
        log: DeliveryLog, 
        webhook_payload: Dict[str, Any], 
        target_url: str,
        secret_key: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Process a webhook delivery attempt
        
        Returns a tuple of (success: bool, status_code: Optional[int], error_details: Optional[str])
        """
        try:
            payload_json = json.dumps(webhook_payload)
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Add signature verification if secret is present (for bonus points)
            if secret_key:
                signature = WebhookDeliveryService._generate_signature(payload_json, secret_key)
                headers['X-Hub-Signature-256'] = f'sha256={signature}'
                
            # Add event type if provided (for bonus points)
            if event_type:
                headers['X-Webhook-Event'] = event_type
            
            # Make HTTP request with timeout
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    target_url, 
                    data=payload_json, 
                    headers=headers,
                    timeout=settings.DELIVERY_TIMEOUT
                ) as response:
                    status_code = response.status
                    if 200 <= status_code < 300:
                        # Successful delivery
                        return True, status_code, None
                    else:
                        # Server responded with an error
                        error_details = f"Target server responded with status {status_code}"
                        response_text = await response.text()
                        if response_text:
                            error_details += f": {response_text[:200]}"  # Truncate long responses
                        return False, status_code, error_details
                        
        except asyncio.TimeoutError:
            return False, None, f"Request timed out after {settings.DELIVERY_TIMEOUT} seconds"
        except aiohttp.ClientError as e:
            return False, None, f"Connection error: {str(e)}"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def _generate_signature(payload: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for payload verification"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    async def handle_delivery_result(
        db: Session,
        log: DeliveryLog,
        success: bool,
        status_code: int,
        error_details: Optional[str]
    ) -> Tuple[DeliveryLog, bool]:
        """
        Handle the result of a webhook delivery attempt
        """
        if success:
            log.status = DeliveryStatus.SUCCESS
            log.status_code = status_code
            should_retry = False
        else:
            # Check if we should retry based on status code
            if status_code in [408, 429, 500, 502, 503, 504]:  # Retryable status codes
                log.status = DeliveryStatus.FAILED_ATTEMPT
                log.attempt_number += 1
                # Implement exponential backoff
                retry_delay = min(300, 2 ** (log.attempt_number - 1))  # Max 5 minutes
                log.next_attempt_at = datetime.utcnow() + timedelta(seconds=retry_delay)
                should_retry = True
            else:
                log.status = DeliveryStatus.FAILURE
                should_retry = False
            
            log.status_code = status_code
            log.error_details = error_details

        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log, should_retry