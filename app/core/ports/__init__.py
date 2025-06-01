# app/core/ports/__init__.py
from .email_sender import EmailSenderInterface
from .subscription_repository import SubscriptionRepositoryInterface
from .payment_gateway import PaymentGatewayInterface # New

__all__ = [
    "EmailSenderInterface",
    "SubscriptionRepositoryInterface",
    "PaymentGatewayInterface"
]
