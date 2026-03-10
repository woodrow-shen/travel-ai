import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.detector import BugFareAlert
from app.email_service import EmailService

logger = logging.getLogger(__name__)

_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
_email_service = EmailService()

# Throttle: don't re-notify the same subscription within this window
NOTIFICATION_COOLDOWN_SECONDS = 6 * 3600  # 6 hours


# ── Helpers ──────────────────────────────────────────────────────────


def _unsubscribe_url(subscription_id: str) -> str:
    token = _serializer.dumps(subscription_id, salt="email-verify")
    return (
        f"{settings.BACKEND_URL}/api/v1/subscriptions/unsubscribe"
        f"?token={token}"
    )


async def _should_notify(subscription) -> bool:
    """Check cooldown: skip if notified recently."""
    if not subscription.is_active:
        return False
    if subscription.last_sent_at:
        elapsed = (
            datetime.now(UTC) - subscription.last_sent_at
        ).total_seconds()
        if elapsed < NOTIFICATION_COOLDOWN_SECONDS:
            logger.debug(
                "Skipping subscription %s — notified %ds ago",
                subscription.id,
                int(elapsed),
            )
            return False
    return True


async def _log_notification(
    db: AsyncSession,
    subscription,
    email: str,
    subject: str,
    success: bool,
) -> None:
    """Write notification log and update last_sent_at."""
    from app.models import NotificationLog, NotificationStatus

    log = NotificationLog(
        subscription_id=subscription.id,
        email=email,
        subject=subject,
        sent_at=datetime.now(UTC),
        status=(
            NotificationStatus.SENT if success else NotificationStatus.FAILED
        ),
    )
    db.add(log)
    if success:
        subscription.last_sent_at = datetime.now(UTC)
    await db.flush()


def _matches_route(
    config: dict,
    origin: str,
    destination: str,
) -> bool:
    """Check if alert origin/destination matches subscription config.

    Config may specify:
      - origins: list of IATA codes (e.g. ["TPE", "TSA"]), empty = any
      - destinations: list of IATA codes, empty = any
    """
    origins = config.get("origins", [])
    destinations = config.get("destinations", [])

    if origins and origin.upper() not in [o.upper() for o in origins]:
        return False
    if destinations and destination.upper() not in [
        d.upper() for d in destinations
    ]:
        return False
    return True


async def _get_user_preferences(
    db: AsyncSession,
    user_id,
) -> dict | None:
    """Load user preferences for filtering. Returns dict or None."""
    from app.models import UserPreference

    stmt = select(UserPreference).where(UserPreference.user_id == user_id)
    result = await db.execute(stmt)
    pref = result.scalar_one_or_none()
    if not pref:
        return None
    return {
        "preferred_airlines": pref.preferred_airlines or [],
        "excluded_airlines": pref.excluded_airlines or [],
        "preferred_alliances": pref.preferred_alliances or [],
        "cabin_classes": pref.cabin_classes or [],
        "max_stops": pref.max_stops,
        "home_airports": pref.home_airports or [],
    }


def _passes_preference_filter(
    prefs: dict | None,
    airline: str | None = None,
    stops: int | None = None,
    origin: str | None = None,
) -> bool:
    """Check if a flight matches user preference filters.

    Returns True if no preferences set or all checks pass.
    """
    if not prefs:
        return True

    # Excluded airlines
    if airline and prefs["excluded_airlines"]:
        if airline.upper() in [a.upper() for a in prefs["excluded_airlines"]]:
            return False

    # Preferred airlines (if set, only notify for these)
    if airline and prefs["preferred_airlines"]:
        if airline.upper() not in [
            a.upper() for a in prefs["preferred_airlines"]
        ]:
            return False

    # Max stops
    if stops is not None and prefs["max_stops"] is not None:
        if stops > prefs["max_stops"]:
            return False

    # Home airports: if set and origin provided, origin must be one of them
    if origin and prefs["home_airports"]:
        if origin.upper() not in [
            a.upper() for a in prefs["home_airports"]
        ]:
            return False

    return True


# ── Send functions ───────────────────────────────────────────────────


async def send_bug_fare_notification(
    db: AsyncSession,
    alert: BugFareAlert,
    subscription,
    email_address: str,
) -> bool:
    """Send a bug fare alert email if cooldown allows."""
    if not await _should_notify(subscription):
        return False

    discount_pct = round(
        (1 - alert.current_price / alert.average_price) * 100
    )
    unsub_url = _unsubscribe_url(str(subscription.id))

    subject = (
        f"Bug Fare! {alert.origin}→{alert.destination} "
        f"{alert.current_price:.0f} {alert.currency}"
    )
    context = {
        "origin": alert.origin,
        "destination": alert.destination,
        "airline": alert.source,
        "departure_date": "",
        "price_amount": f"{alert.current_price:,.0f}",
        "price_currency": alert.currency,
        "avg_price": f"{alert.average_price:,.0f}",
        "discount_pct": discount_pct,
        "confidence": alert.confidence,
        "unsubscribe_url": unsub_url,
    }

    success = await _email_service.send_email(
        to=email_address,
        subject=subject,
        template_name="bug_fare_alert.html",
        context=context,
    )
    await _log_notification(
        db, subscription, email_address, subject, success
    )
    return success


async def send_price_drop_notification(
    db: AsyncSession,
    origin: str,
    destination: str,
    current_price: float,
    previous_price: float,
    target_price: float,
    currency: str,
    subscription,
    email_address: str,
) -> bool:
    """Send a price drop alert email if cooldown allows."""
    if not await _should_notify(subscription):
        return False

    unsub_url = _unsubscribe_url(str(subscription.id))

    subject = (
        f"Price Drop! {origin}→{destination} "
        f"{current_price:.0f} {currency}"
    )
    context = {
        "origin": origin,
        "destination": destination,
        "departure_date": "",
        "previous_price": f"{previous_price:,.0f}",
        "current_price": f"{current_price:,.0f}",
        "target_price": f"{target_price:,.0f}",
        "price_currency": currency,
        "unsubscribe_url": unsub_url,
    }

    success = await _email_service.send_email(
        to=email_address,
        subject=subject,
        template_name="price_drop_alert.html",
        context=context,
    )
    await _log_notification(
        db, subscription, email_address, subject, success
    )
    return success


async def send_deal_digest(
    db: AsyncSession,
    subscription,
    email_address: str,
    deals: list[dict],
) -> bool:
    """Send a deal digest email.

    Each deal dict should have: origin, destination, airline,
    departure_date, price, currency, tags (optional list).
    """
    if not await _should_notify(subscription):
        return False
    if not deals:
        return False

    unsub_url = _unsubscribe_url(str(subscription.id))
    subject = f"Travel-AI Deal Digest — {len(deals)} deals found"
    context = {
        "deals": deals,
        "unsubscribe_url": unsub_url,
    }

    success = await _email_service.send_email(
        to=email_address,
        subject=subject,
        template_name="deal_digest.html",
        context=context,
    )
    await _log_notification(
        db, subscription, email_address, subject, success
    )
    return success


# ── Trigger + filter functions ───────────────────────────────────────


async def check_and_notify_bug_fares(
    db: AsyncSession,
    alert: BugFareAlert,
) -> int:
    """Find active bug_fare subscriptions, apply route + preference
    filters, and notify matching ones.

    Config fields:
      - min_discount: minimum discount % to trigger (default 0)
      - origins: list of IATA codes (empty = any)
      - destinations: list of IATA codes (empty = any)
    """
    from app.models import Subscription, SubscriptionType

    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.subscription_email))
        .where(
            Subscription.type == SubscriptionType.BUG_FARE,
            Subscription.is_active.is_(True),
        )
    )
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()

    sent = 0
    for sub in subscriptions:
        email = sub.subscription_email
        if not email or not email.is_verified:
            continue

        config = sub.config or {}

        # Route filter
        if not _matches_route(config, alert.origin, alert.destination):
            continue

        # Discount threshold
        min_discount = config.get("min_discount", 0)
        actual_discount = (
            (1 - alert.current_price / alert.average_price) * 100
            if alert.average_price > 0
            else 0
        )
        if actual_discount < min_discount:
            continue

        # User preference filter
        prefs = await _get_user_preferences(db, sub.user_id)
        if not _passes_preference_filter(
            prefs,
            airline=alert.source,
            origin=alert.origin,
        ):
            continue

        success = await send_bug_fare_notification(
            db, alert, sub, email.email
        )
        if success:
            sent += 1

    logger.info(
        "Bug fare %s→%s: notified %d/%d subscriptions",
        alert.origin,
        alert.destination,
        sent,
        len(subscriptions),
    )
    return sent


async def check_and_notify_price_drops(
    db: AsyncSession,
    origin: str,
    destination: str,
    current_price: float,
    previous_price: float,
    currency: str,
    airline: str | None = None,
    stops: int | None = None,
) -> int:
    """Find active price_drop subscriptions, apply route + preference
    filters, and notify if price dropped below target.

    Config fields:
      - origin: IATA code (optional route filter)
      - destination: IATA code (optional route filter)
      - target_price: price threshold to trigger notification
    """
    from app.models import Subscription, SubscriptionType

    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.subscription_email))
        .where(
            Subscription.type == SubscriptionType.PRICE_DROP,
            Subscription.is_active.is_(True),
        )
    )
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()

    sent = 0
    for sub in subscriptions:
        email = sub.subscription_email
        if not email or not email.is_verified:
            continue

        config = sub.config or {}
        target_price = config.get("target_price", previous_price)

        # Route filter
        sub_origin = config.get("origin")
        sub_dest = config.get("destination")
        if sub_origin and sub_origin.upper() != origin.upper():
            continue
        if sub_dest and sub_dest.upper() != destination.upper():
            continue

        # Price threshold
        if current_price > target_price:
            continue

        # User preference filter
        prefs = await _get_user_preferences(db, sub.user_id)
        if not _passes_preference_filter(
            prefs,
            airline=airline,
            stops=stops,
            origin=origin,
        ):
            continue

        success = await send_price_drop_notification(
            db,
            origin=origin,
            destination=destination,
            current_price=current_price,
            previous_price=previous_price,
            target_price=target_price,
            currency=currency,
            subscription=sub,
            email_address=email.email,
        )
        if success:
            sent += 1

    logger.info(
        "Price drop %s→%s: notified %d/%d subscriptions",
        origin,
        destination,
        sent,
        len(subscriptions),
    )
    return sent


@dataclass
class DealItem:
    """A single deal for digest emails."""

    origin: str
    destination: str
    airline: str
    departure_date: str
    price: float
    currency: str
    tags: list[str] | None = None


async def check_and_send_deal_digests(
    db: AsyncSession,
    available_deals: list[DealItem],
) -> int:
    """Find active deal_digest subscriptions, filter deals by user
    preferences, and send digest emails.

    Config fields:
      - frequency: "daily" or "weekly" (caller decides when to invoke)
      - preferred_destinations: list of IATA codes (empty = any)
    """
    from app.models import Subscription, SubscriptionType

    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.subscription_email))
        .where(
            Subscription.type == SubscriptionType.DEAL_DIGEST,
            Subscription.is_active.is_(True),
        )
    )
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()

    sent = 0
    for sub in subscriptions:
        email = sub.subscription_email
        if not email or not email.is_verified:
            continue

        config = sub.config or {}
        pref_dests = [
            d.upper() for d in config.get("preferred_destinations", [])
        ]

        # User preference filter
        prefs = await _get_user_preferences(db, sub.user_id)

        # Filter deals for this subscription
        filtered: list[dict] = []
        for deal in available_deals:
            # Destination filter from subscription config
            if pref_dests and deal.destination.upper() not in pref_dests:
                continue

            # User preference filter (airline, stops, home airport)
            if not _passes_preference_filter(
                prefs,
                airline=deal.airline,
                origin=deal.origin,
            ):
                continue

            filtered.append({
                "origin": deal.origin,
                "destination": deal.destination,
                "airline": deal.airline,
                "departure_date": deal.departure_date,
                "price": f"{deal.price:,.0f}",
                "currency": deal.currency,
                "tags": deal.tags or [],
            })

        if not filtered:
            continue

        # Limit to top 10 deals (already sorted by caller)
        filtered = filtered[:10]

        success = await send_deal_digest(
            db, sub, email.email, filtered
        )
        if success:
            sent += 1

    logger.info(
        "Deal digest: notified %d/%d subscriptions (%d deals available)",
        sent,
        len(subscriptions),
        len(available_deals),
    )
    return sent
