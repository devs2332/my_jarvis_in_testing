"""Pydantic schemas for billing."""

from pydantic import BaseModel
from typing import Optional


class CheckoutRequest(BaseModel):
    plan: str  # "pro" or "enterprise"
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class SubscriptionResponse(BaseModel):
    plan: str
    status: str
    billing_cycle_start: Optional[str] = None
    billing_cycle_end: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

    model_config = {"from_attributes": True}


class UsageResponse(BaseModel):
    total_tokens: int
    total_cost_usd: float
    token_limit: int
    usage_percentage: float
    breakdown_by_model: dict
