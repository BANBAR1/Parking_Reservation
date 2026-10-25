from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Protocol

from parking_reservation.errors import (
    ReversedBookingTimeError,
    SpotIsNotInGivenLotError,
)
from parking_reservation.models.parking import ParkingLot, ParkingSpot
from parking_reservation.timekeeping import as_utc, get_hours


@dataclass(frozen=True)
class Driver:
    name: str


@dataclass(frozen=True)
class Vehicle:
    license_plate: str
    driver: Driver


class PricingRule(Protocol):
    def calculate(self, rate: Decimal, duration: timedelta) -> Decimal: ...


class BookingStatus(Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"


@dataclass
class Booking:
    lot: ParkingLot
    spot: ParkingSpot
    vehicle: Vehicle
    start_time: datetime
    end_time: datetime
    pricing_rule: PricingRule
    hourly_rate: Decimal
    total: Decimal = field(init=False)
    status: BookingStatus = field(default=BookingStatus.ACTIVE, init=False)

    def __post_init__(self) -> None:
        self.start_time = as_utc(self.start_time, "start_time")
        self.end_time = as_utc(self.end_time, "end_time")

        if self.end_time <= self.start_time:
            raise ReversedBookingTimeError

        if not any(lot_spot is self.spot for lot_spot in self.lot.spots):
            raise SpotIsNotInGivenLotError

        self.total = self._cost_at_creation()

    def _cost_at_creation(self) -> Decimal:
        duration = self.end_time - self.start_time
        return self.pricing_rule.calculate(rate=self.hourly_rate, duration=duration)

    def duration_hours(self) -> Decimal:
        return get_hours(self.end_time - self.start_time)

    def cancel(self) -> None:
        self.status = BookingStatus.CANCELLED
