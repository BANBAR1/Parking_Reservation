from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

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
    hourly_rate: Decimal
    total: Decimal
    status: BookingStatus = field(default=BookingStatus.ACTIVE)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.start_time = as_utc(self.start_time, "start_time")
        self.end_time = as_utc(self.end_time, "end_time")

        if self.end_time <= self.start_time:
            raise ReversedBookingTimeError

        if self.spot not in self.lot.spots:
            raise SpotIsNotInGivenLotError

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Booking) and other.id == self.id

    def duration_hours(self) -> Decimal:
        return get_hours(self.end_time - self.start_time)

    def cancel(self) -> None:
        self.status = BookingStatus.CANCELLED
