from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from parking_reservation.errors import TimezoneError


def as_utc(value: datetime, what: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise TimezoneError(f"{what} must be timezone-aware")
    return value.astimezone(UTC)


def as_utc_from(value: datetime, zone: ZoneInfo, what: str) -> datetime:
    if value.tzinfo != zone:
        raise TimezoneError(f"{what} must use the lot's timezone")

    instant = value.astimezone(UTC)
    if instant.astimezone(zone).replace(tzinfo=None) != value.replace(tzinfo=None):
        raise TimezoneError(f"{what} is not a valid local time")

    return instant
