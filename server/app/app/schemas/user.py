"""Pydantic schemas for user management."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None


class UserAdminUpdateRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserListResponse(BaseModel):
    users: list
    total: int
    page: int
    per_page: int
