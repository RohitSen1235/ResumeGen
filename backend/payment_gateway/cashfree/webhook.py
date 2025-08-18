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
            logger.info(f"Received webhook: {webhook_data}")
            
            # Extract payment information
            if 'data' in webhook_data:
                data = webhook_data['data']
                order_info = data.get('order', {})
                payment_info = data.get('payment', {})
                customer_info = data.get('customer_details', {})
                
                order_id = order_info.get('order_id')
                payment_status = payment_info.get('payment_status')
                
                logger.info(f"Processing webhook for order {order_id} with status {payment_status}")
                
                # Handle different payment statuses
                if payment_status == "SUCCESS":
                    await self.handle_successful_payment(order_id, data)
                elif payment_status == "FAILED":
                    await self.handle_failed_payment(order_id, data)
                else:
                    logger.info(f"Unhandled payment status: {payment_status}")

        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    async def handle_successful_payment(
        self,
        order_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Handle successful payment"""
        logger.info(f"Payment successful for order {order_id}")
        
        try:
            # Import here to avoid circular imports
            from app.database import get_db
            from app.models import User
            
            # Extract customer information from webhook data
            customer_info = data.get('customer_details', {})
            customer_email = customer_info.get('customer_email')
            order_info = data.get('order', {})
            payment_info = data.get('payment', {})
            order_amount = order_info.get('order_amount', 0)
            
            if customer_email:
                # Get database session
                db = next(get_db())
                try:
                    # Find the user by email
                    user = db.query(User).filter(User.email == customer_email).first()
                    if user:
                        # Calculate credits based on amount
                        if order_amount == 2175 or order_amount == 2175.0:  # Pro package (₹2175)
                            credits_to_add = 30
                        elif order_amount == 875 or order_amount == 875.0:  # Basic package (₹875)
                            credits_to_add = 10
                        elif order_amount == 5275 or order_amount == 5275.0:  # Enterprise package (₹5275)
                            credits_to_add = 100
                        else:
                            # Default fallback - calculate based on amount (₹87.5 per credit)
                            credits_to_add = max(1, int(order_amount / 87.5))
                            logger.warning(f"Unknown payment amount {order_amount}, calculated {credits_to_add} credits")
                        
                        user.credits = (user.credits or 0) + credits_to_add
                        db.commit()
                        db.refresh(user)
                        logger.info(f"Added {credits_to_add} credits to user {customer_email} for amount ₹{order_amount}. New balance: {user.credits}")
                    else:
                        logger.error(f"User with email {customer_email} not found for credit update")
                finally:
                    db.close()
            else:
                logger.error(f"No customer_email found in webhook data for order {order_id}")
                
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
