"""
Billing API endpoints — Stripe checkout, portal, and webhooks.
"""

import logging
from fastapi import APIRouter, HTTPException, Request, status

from server.app.dependencies import DBSession, CurrentUser
from server.app.schemas.billing import (
    CheckoutRequest, CheckoutResponse, SubscriptionResponse,
)
from server.app.services.billing_service import (
    create_checkout_session, create_billing_portal,
    handle_webhook_event, get_user_subscription,
)
from server.app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(request: CheckoutRequest, user: CurrentUser, db: DBSession):
    """Create a Stripe checkout session for plan upgrade."""
    try:
        result = await create_checkout_session(
            db, user, request.plan, request.success_url, request.cancel_url,
        )
        return CheckoutResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session",
        )


@router.post("/portal")
async def billing_portal(user: CurrentUser, db: DBSession):
    """Create a Stripe billing portal session."""
    url = await create_billing_portal(
        db, user, return_url="http://localhost:5173/dashboard"
    )
    return {"portal_url": url}


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(user: CurrentUser, db: DBSession):
    """Get the current user's subscription details."""
    sub = await get_user_subscription(db, user.id)
    if not sub:
        return SubscriptionResponse(plan="free", status="active")
    return SubscriptionResponse(
        plan=sub.plan.value,
        status=sub.status.value,
        billing_cycle_start=(
            sub.billing_cycle_start.isoformat() if sub.billing_cycle_start else None
        ),
        billing_cycle_end=(
            sub.billing_cycle_end.isoformat() if sub.billing_cycle_end else None
        ),
        stripe_subscription_id=sub.stripe_subscription_id,
    )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: DBSession):
    """Handle Stripe webhook events."""
    import stripe

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    await handle_webhook_event(db, event)
    return {"status": "ok"}
