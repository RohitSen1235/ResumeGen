class CashfreePaymentError(Exception):
    """Base exception for Cashfree payment errors"""
    pass


class OrderCreationError(CashfreePaymentError):
    """Failed to create payment order"""
    pass


class PaymentStatusError(CashfreePaymentError):
    """Failed to get payment status"""
    pass


class WebhookVerificationError(CashfreePaymentError):
    """Failed to verify webhook signature"""
    pass


class InvalidRequestError(CashfreePaymentError):
    """Invalid request parameters"""
    pass


class PaymentProcessingError(CashfreePaymentError):
    """Payment processing failed"""
    pass


class PaymentTimeoutError(CashfreePaymentError):
    """Payment processing timed out"""
    pass
