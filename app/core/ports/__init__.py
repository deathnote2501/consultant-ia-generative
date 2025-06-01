# app/core/ports/__init__.py
from .email_sender import EmailSenderInterface
from .subscription_repository import SubscriptionRepositoryInterface # New import

__all__ = ["EmailSenderInterface", "SubscriptionRepositoryInterface"] # Add new interface to __all__
