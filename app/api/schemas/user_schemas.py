from pydantic import BaseModel, EmailStr

class SubmitEmailRequest(BaseModel):
    email: EmailStr

class MessageResponse(BaseModel): # A generic response model for simple messages
    message: str
