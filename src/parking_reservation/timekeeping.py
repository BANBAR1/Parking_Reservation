from datetime import UTC, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from parking_reservation.errors import InvalidTimezoneError


def get_microseconds(duration: timedelta) -> int:
    return duration // timedelta(microseconds=1)


def get_hours(duration: timedelta) -> Decimal:
    return Decimal(get_microseconds(duration)) / Decimal("3600000000")


def as_utc(value: datetime, what: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise InvalidTimezoneError(f"{what} must be timezone-aware")
    return value.astimezone(UTC)


def as_utc_from(value: datetime, zone: ZoneInfo, what: str) -> datetime:
    if value.tzinfo != zone:
        raise InvalidTimezoneError(f"{what} must use the lot's timezone")

    instant = value.astimezone(UTC)
    if instant.astimezone(zone).replace(tzinfo=None) != value.replace(tzinfo=None):
        raise InvalidTimezoneError(f"{what} is not a valid local time")

    return instant
