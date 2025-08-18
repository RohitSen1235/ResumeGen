import os
import json
import logging
from typing import Dict, Optional
import httpx

from .exceptions import CashfreePaymentError
from .schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
    PaymentStatusResponse
)

logger = logging.getLogger(__name__)


class CashfreeClient:
    BASE_URL = "https://sandbox.cashfree.com/pg"  # Test environment
    
    def __init__(
        self,
        app_id: str,
        secret_key: str,
        api_version: str = "2023-08-01"
    ):
        self.app_id = app_id
        self.secret_key = secret_key
        self.api_version = api_version
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-version": self.api_version,
                "x-client-id": self.app_id,
                "x-client-secret": self.secret_key
            }
        )

    async def create_order(
        self,
        request: CreateOrderRequest
    ) -> CreateOrderResponse:
        """Create a new payment order with Cashfree"""
        endpoint = "/orders"
        try:
            payload = request.model_dump(exclude_none=True)
            logger.info(f"Sending payload to Cashfree: {json.dumps(payload, indent=2)}")
            
            response = await self.client.post(
                endpoint,
                json=payload
            )
            response.raise_for_status()
            
            response_data = response.json()
            logger.info(f"Cashfree response: {json.dumps(response_data, indent=2)}")
            
            return CreateOrderResponse(**response_data)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Cashfree API error: {str(e)}")
            raise CashfreePaymentError(
                f"Order creation failed: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error creating order: {str(e)}")
            raise CashfreePaymentError("Failed to create payment order")

    async def get_payment_status(
        self,
        order_id: str
    ) -> PaymentStatusResponse:
        """Get payment status for an order"""
        endpoint = f"/orders/{order_id}/payments"
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return PaymentStatusResponse(**response.json())
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Cashfree API error: {str(e)}")
            raise CashfreePaymentError(
                f"Status check failed: {e.response.text}"
            )

    async def verify_webhook(
        self,
        signature: str,
        payload: Dict
    ) -> bool:
        """Verify webhook signature"""
        # Implementation depends on Cashfree's webhook verification logic
        # This is a placeholder - actual implementation would verify the signature
        return True

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
