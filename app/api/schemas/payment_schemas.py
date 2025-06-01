from pydantic import BaseModel, Field

class CreateCheckoutSessionRequest(BaseModel):
    plan_id: str = Field(..., description="The ID of the Stripe Price (e.g., price_xxxxxxxxxxxxxx)")

class CreateCheckoutSessionResponse(BaseModel):
    checkout_session_id: str
