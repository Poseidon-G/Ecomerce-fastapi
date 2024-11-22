# UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from typing import Optional, List
from datetime import datetime
from app.models.model import UserRole
from pydantic import BaseModel, Field, ConfigDict

class UserBase(BaseModel):
    email: str = Field(..., min_length=2, max_length=100, description="User email")
    password: str = Field(..., min_length=6, description="User password")
    first_name: str = Field(..., min_length=2, max_length=50, description="User first name")
    last_name: str = Field(..., min_length=2, max_length=50, description="User last name")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="User role")
    is_active: bool = Field(default=True, description="User status")


class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, min_length=2, max_length=100, description="User email")
    first_name: Optional[str] = Field(None, min_length=2, max_length=50, description="User first name")
    last_name: Optional[str] = Field(None, min_length=2, max_length=50, description="User last name")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    role: Optional[UserRole] = Field(None, description="User role")

class UserResponse(UserBase):
    id: int
    created_at: datetime
    created_at: datetime
    updated_at: str
    model_config = ConfigDict(from_attributes=True)


class UserPasswordUpdate(BaseModel):
    old_password: str = Field(..., min_length=6, description="Old password")
    new_password: str = Field(..., min_length=6, description="New password")
    confirm_password: str = Field(..., min_length=6, description="Confirm new password")
    model_config = ConfigDict(from_attributes=True)

class UserDeactivate(BaseModel):
    is_active: bool = Field(default=False, description="User status")
    model_config = ConfigDict(from_attributes=True)
    