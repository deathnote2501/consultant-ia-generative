from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str # Assuming fastapi-users setup provides a refresh token
    token_type: str = "bearer"
