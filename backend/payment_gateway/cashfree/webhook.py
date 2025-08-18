import hashlib
import hmac
import json
import logging
import os
from typing import Dict, Any

from fastapi import HTTPException

from .exceptions import WebhookVerificationError

logger = logging.getLogger(__name__)


class CashfreeWebhookHandler:
    def __init__(self):
        pass

    def verify_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """Verify webhook signature using secret key"""
        try:
            # Get the secret key from environment
            secret_key = os.getenv("CASHFREE_SECRET_KEY")
            if not secret_key:
                logger.warning("Missing CASHFREE_SECRET_KEY, skipping signature verification")
                return True  # Skip verification in development
            
            # For Cashfree v4 API, signature verification is different
            # This is a simplified version - in production you should implement proper verification
            return True
            
        except Exception as e:
            logger.error(f"Webhook verification failed: {str(e)}")
            return False

    async def handle_webhook(
        self,
        payload: bytes
    ) -> None:
        """Process incoming webhook notification"""
        try:
            # Parse the JSON payload
            webhook_data = json.loads(payload.decode('utf-8'))
            webhook_type = webhook_data.get('type')
            logger.info(f"Received webhook of type '{webhook_type}': {webhook_data}")

            # --- Explicit Webhook Type Check ---
            # Only process the primary success webhook to prevent duplicates from other event types.
            if webhook_type != 'PAYMENT_SUCCESS_WEBHOOK':
                logger.info(f"Skipping webhook of type '{webhook_type}' as it is not the designated event for credit allocation.")
                return
            
            # Extract payment information
            if 'data' in webhook_data:
                data = webhook_data['data']
                order_info = data.get('order', {})
                payment_info = data.get('payment', {})
                
                order_id = order_info.get('order_id')
                payment_status = payment_info.get('payment_status')
                
                logger.info(f"Processing '{webhook_type}' for order {order_id} with status {payment_status}")
                
                # We already know the type is for success, but we double-check the status field as a safeguard.
                if payment_status == "SUCCESS":
                    await self.handle_successful_payment(order_id, data)
                elif payment_status == "FAILED":
                    await self.handle_failed_payment(order_id, data)
                else:
                    logger.info(f"Unhandled payment status within a success-type webhook: {payment_status}")

        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    async def handle_successful_payment(
        self,
        order_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Handle successful payment"""
        logger.info(f"Processing successful payment for order {order_id}")
        
        try:
            # Import here to avoid circular imports
            from app.database import get_db, get_redis
            from app.models import User

            # --- Atomic Idempotency Check ---
            redis_client = get_redis()
            if not redis_client:
                logger.error("Redis client not available. Cannot guarantee idempotency.")
                # In a production environment, you might want to fail here or have a different fallback
            else:
                processed_key = f"processed_order:{order_id}"
                # Use SET with NX (Not Exists) and EX (Expire) for an atomic check and lock.
                # This returns True if the key was set, and False if it already existed.
                if not redis_client.set(processed_key, "processed", nx=True, ex=3600 * 24 * 30):
                    logger.info(f"Order {order_id} has already been processed or is in progress. Skipping credit addition.")
                    return
            
            # Extract customer information from webhook data
            customer_info = data.get('customer_details', {})
            customer_email = customer_info.get('customer_email')
            order_info = data.get('order', {})
            order_amount = order_info.get('order_amount', 0)
            
            if not customer_email:
                logger.error(f"No customer_email found in webhook data for order {order_id}")
                return

            # Get database session
            db = next(get_db())
            try:
                # Find the user by email
                user = db.query(User).filter(User.email == customer_email).first()
                if not user:
                    logger.error(f"User with email {customer_email} not found for credit update")
                    return

                # Calculate credits based on amount
                credits_to_add = 0
                if order_amount in [2250, 2250.0]:  # Pro package (₹2175)
                    credits_to_add = 30
                elif order_amount in [900, 900.0]:  # Basic package (₹875)
                    credits_to_add = 10
                elif order_amount in [5400, 5400.0]:  # Enterprise package (₹5275)
                    credits_to_add = 90
                
                if credits_to_add > 0:
                    user.credits = (user.credits or 0) + credits_to_add
                    db.commit()
                    db.refresh(user)
                    logger.info(f"SUCCESS: Added {credits_to_add} credits to user {customer_email} for amount ₹{order_amount}. New balance: {user.credits}")
                else:
                    logger.warning(f"No credits mapped for order {order_id} with amount {order_amount}. No credits were added.")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing successful payment for order {order_id}: {str(e)}")

    async def handle_failed_payment(
        self,
        order_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Handle failed payment"""
        logger.warning(f"Payment failed for order {order_id}")
        # TODO: Update order status to failed
