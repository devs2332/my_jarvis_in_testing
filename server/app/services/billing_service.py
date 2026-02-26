"""
Billing service — Stripe integration for subscription management.
"""

import logging
from typing import Optional
from datetime import datetime, timezone

import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from server.app.config import get_settings
from server.app.models.subscription import Subscription, PlanType, SubscriptionStatus
from server.app.models.user import User
from server.app.core.audit_log import audit_log

logger = logging.getLogger(__name__)
settings = get_settings()

stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_PRICE_MAP = {
    "pro": settings.STRIPE_PRICE_PRO,
    "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
}


async def get_or_create_stripe_customer(
    db: AsyncSession, user: User
) -> str:
    """Get or create a Stripe customer for the user."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    sub = result.scalar_one_or_none()

    if sub and sub.stripe_customer_id:
        return sub.stripe_customer_id

    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name or user.email,
        metadata={"user_id": str(user.id)},
    )

    if sub:
        sub.stripe_customer_id = customer.id
    else:
        sub = Subscription(
            user_id=user.id,
            plan=PlanType.FREE,
            status=SubscriptionStatus.ACTIVE,
            stripe_customer_id=customer.id,
        )
        db.add(sub)

    await db.flush()
    return customer.id


async def create_checkout_session(
    db: AsyncSession,
    user: User,
    plan: str,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Create a Stripe Checkout session for a plan upgrade."""
    price_id = PLAN_PRICE_MAP.get(plan)
    if not price_id:
        raise ValueError(f"Invalid plan: {plan}")

    customer_id = await get_or_create_stripe_customer(db, user)

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": str(user.id), "plan": plan},
    )

    audit_log("checkout_session_created", user_id=str(user.id),
              detail={"plan": plan, "session_id": session.id})

    return {"checkout_url": session.url, "session_id": session.id}


async def create_billing_portal(
    db: AsyncSession, user: User, return_url: str
) -> str:
    """Create a Stripe Billing Portal session."""
    customer_id = await get_or_create_stripe_customer(db, user)

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


async def handle_webhook_event(
    db: AsyncSession, event: dict
) -> None:
    """Process Stripe webhook events."""
    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(db, data)
    elif event_type == "customer.subscription.updated":
        await _handle_subscription_updated(db, data)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(db, data)
    elif event_type == "invoice.payment_failed":
        await _handle_payment_failed(db, data)


async def _handle_checkout_completed(db: AsyncSession, data: dict):
    """Activate subscription after successful checkout."""
    user_id = data.get("metadata", {}).get("user_id")
    plan = data.get("metadata", {}).get("plan", "pro")
    stripe_sub_id = data.get("subscription")

    if not user_id:
        return

    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    sub = result.scalar_one_or_none()

    if sub:
        sub.plan = PlanType(plan)
        sub.status = SubscriptionStatus.ACTIVE
        sub.stripe_subscription_id = stripe_sub_id
        sub.billing_cycle_start = datetime.now(timezone.utc)
        await db.flush()

    audit_log("subscription_activated", user_id=user_id, detail={"plan": plan})


async def _handle_subscription_updated(db: AsyncSession, data: dict):
    """Update subscription status on Stripe changes."""
    stripe_sub_id = data.get("id")
    status = data.get("status", "active")

    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_sub_id
        )
    )
    sub = result.scalar_one_or_none()

    if sub:
        status_map = {
            "active": SubscriptionStatus.ACTIVE,
            "past_due": SubscriptionStatus.PAST_DUE,
            "canceled": SubscriptionStatus.CANCELED,
            "trialing": SubscriptionStatus.TRIALING,
        }
        sub.status = status_map.get(status, SubscriptionStatus.ACTIVE)
        await db.flush()


async def _handle_subscription_deleted(db: AsyncSession, data: dict):
    """Downgrade to free plan when subscription is canceled."""
    stripe_sub_id = data.get("id")

    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_sub_id
        )
    )
    sub = result.scalar_one_or_none()

    if sub:
        sub.plan = PlanType.FREE
        sub.status = SubscriptionStatus.ACTIVE
        sub.stripe_subscription_id = None
        await db.flush()

    audit_log("subscription_canceled", detail={"stripe_subscription_id": stripe_sub_id})


async def _handle_payment_failed(db: AsyncSession, data: dict):
    """Mark subscription as past due on failed payments."""
    customer_id = data.get("customer")

    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_customer_id == customer_id
        )
    )
    sub = result.scalar_one_or_none()

    if sub:
        sub.status = SubscriptionStatus.PAST_DUE
        await db.flush()

    logger.warning(f"Payment failed for customer {customer_id}")


async def get_user_subscription(
    db: AsyncSession, user_id
) -> Optional[Subscription]:
    """Get the user's current subscription."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    return result.scalar_one_or_none()
