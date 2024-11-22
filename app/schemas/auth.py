from pydantic import BaseModel, Field, ConfigDict


class TokenPayload(BaseModel):
    exp: float = None
    sub: str = None
    type: str = None
    iat: float = None
    jti: str = None
    model_config = ConfigDict(from_attributes=True)




class LoginBody(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str = None
    token_type: str = "bearer"