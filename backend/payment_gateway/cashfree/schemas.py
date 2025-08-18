from typing import Optional, Dict, List
from enum import Enum
from pydantic import BaseModel, Field


class PaymentMethod(str, Enum):
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"
    PAYLATER = "paylater"


class CustomerDetails(BaseModel):
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: str


class OrderMeta(BaseModel):
    return_url: Optional[str] = Field(None, description="URL to redirect after payment")
    notify_url: Optional[str] = Field(None, description="Webhook URL for payment notifications")
    payment_methods: Optional[str] = None


class CreateOrderRequest(BaseModel):
    order_amount: float
    order_currency: str
    customer_details: CustomerDetails
    order_meta: OrderMeta
    order_id: Optional[str] = None
    order_note: Optional[str] = None
    order_tags: Optional[Dict[str, str]] = None


class PaymentMethodDetails(BaseModel):
    method: PaymentMethod
    card: Optional[Dict] = None
    upi: Optional[Dict] = None
    netbanking: Optional[Dict] = None


class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"


class PaymentDetails(BaseModel):
    payment_id: str
    payment_amount: float
    payment_currency: str
    payment_status: PaymentStatus
    payment_method: PaymentMethodDetails
    payment_time: Optional[str] = None


class CreateOrderResponse(BaseModel):
    order_id: str
    payment_link: Optional[str] = None
    payment_session_id: Optional[str] = None
    cf_order_id: str
    order_status: str


class PaymentStatusResponse(BaseModel):
    order_id: str
    order_amount: float
    order_status: str
    payments: List[PaymentDetails]


class WebhookPayload(BaseModel):
    order_id: str
    order_amount: float
    reference_id: str
    tx_status: str
    payment_mode: str
    tx_msg: str
    tx_time: str
    signature: str
