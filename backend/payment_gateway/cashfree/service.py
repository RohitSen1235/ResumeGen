import os
from typing import Optional, Dict
from datetime import datetime
import logging

from fastapi import HTTPException
from pydantic import BaseModel

from .client import CashfreeClient
from .exceptions import CashfreePaymentError
from .schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
    PaymentStatusResponse,
    CustomerDetails,
    OrderMeta
)

logger = logging.getLogger(__name__)


class CashfreePaymentService:
    def __init__(self):
        self.client = CashfreeClient(
            app_id=os.getenv("CASHFREE_APP_ID"),
            secret_key=os.getenv("CASHFREE_SECRET_KEY"),
            api_version=os.getenv("CASHFREE_API_VERSION")
        )

    async def create_order(
        self,
        amount: float,
        customer_details: Dict,
        order_meta: Optional[Dict] = None,
        order_id: Optional[str] = None,
        order_note: Optional[str] = None,
        order_tags: Optional[Dict[str, str]] = None
    ) -> CreateOrderResponse:
        """Create a new Cashfree payment order"""
        try:
            request = CreateOrderRequest(
                order_amount=amount,
                customer_details=CustomerDetails(**customer_details),
                order_meta=OrderMeta(**order_meta) if order_meta else OrderMeta(),
                order_id=order_id,
                order_currency="INR",
                order_note=order_note or f"ResumeGen subscription - {datetime.now().isoformat()}",
                order_tags=order_tags
            )
            
            response = await self.client.create_order(request)
            return response
            
        except CashfreePaymentError as e:
            logger.error(f"Cashfree order creation failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Payment processing error: {str(e)}"
            )

    async def get_payment_status(
        self,
        order_id: str
    ) -> PaymentStatusResponse:
        """Check the status of a payment"""
        try:
            return await self.client.get_payment_status(order_id)
        except CashfreePaymentError as e:
            logger.error(f"Cashfree status check failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Payment status check failed: {str(e)}"
            )

    async def verify_webhook(
        self,
        signature: str,
        payload: Dict
    ) -> bool:
        """Verify webhook signature"""
        return await self.client.verify_webhook(signature, payload)
