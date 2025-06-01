# app/api/schemas/__init__.py
from .user_schemas import SubmitEmailRequest, MessageResponse # Existing
from .auth_schemas import TokenResponse # New

__all__ = ["SubmitEmailRequest", "MessageResponse", "TokenResponse"]
