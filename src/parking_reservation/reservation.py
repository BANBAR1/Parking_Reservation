from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from parking_reservation import booking_file
from parking_reservation.errors import (
    BookingCancellationError,
    BookingNotFoundError,
    BookingTimeInPastError,
    LotIsNotOpenError,
    SpotAlreadyBookedError,
    SpotOutOfServiceError,
)
from parking_reservation.models import (
    Booking,
    BookingStatus,
    LotCollection,
    LotStatus,
    ParkingLot,
    ParkingSpot,
    Vehicle,
)
from parking_reservation.pricing import rate_for, rule_for
from parking_reservation.timekeeping import as_utc_from


class BookingRepository(Protocol):
    def all(self) -> list[Booking]: ...

    def add(self, booking: Booking) -> None: ...

    def update(self, booking: Booking) -> None: ...


@dataclass
class BookingFile:
    path: Path
    lots: LotCollection
    _bookings: list[Booking] = field(default_factory=list[Booking], init=False)

    def __post_init__(self) -> None:
        try:
            self._bookings: list[Booking] = booking_file.load(self.path, self.lots)
        except FileNotFoundError:
            self._bookings = []

    def all(self) -> list[Booking]:
        return self._bookings.copy()

    def add(self, booking: Booking) -> None:
        self._bookings.append(booking)
        booking_file.save(self._bookings, self.path)

    def update(self, booking: Booking) -> None:
        booking_file.save(self._bookings, self.path)


@dataclass
class BookingMemory:
    _bookings: list[Booking] = field(default_factory=list[Booking])

    def all(self) -> list[Booking]:
        return self._bookings.copy()

    def add(self, booking: Booking) -> None:
        self._bookings.append(booking)

    def update(self, booking: Booking) -> None:
        pass


@dataclass(frozen=True)
class BookingRequest:
    lot: ParkingLot
    spot: ParkingSpot
    vehicle: Vehicle
    start_time: datetime
    end_time: datetime

    def __post_init__(self) -> None:
        zone = self.lot.location.timezone
        object.__setattr__(self, "start_time", as_utc_from(self.start_time, zone, "start_time"))
        object.__setattr__(self, "end_time", as_utc_from(self.end_time, zone, "end_time"))


@dataclass
class ReservationService:
    storage: BookingRepository
    clock: Callable[[], datetime] = lambda: datetime.now(UTC)

    @property
    def bookings(self) -> list[Booking]:
        return self.storage.all()

    def reserve(self, request: BookingRequest) -> Booking:
        lot = request.lot
        spot = request.spot
        vehicle = request.vehicle
        start_time = request.start_time
        end_time = request.end_time
        rate = rate_for(spot.type)
        rule = rule_for(spot.type)
        total = rule.calculate(rate=rate, duration=end_time - start_time)

        booking = Booking(
            lot=lot,
            spot=spot,
            vehicle=vehicle,
            start_time=start_time,
            end_time=end_time,
            hourly_rate=rate,
            total=total,
        )

        self._validate_request(request)
        self.storage.add(booking)

        return booking

    def cancel(self, booking: Booking) -> None:
        for held_booking in self.storage.all():
            if held_booking is booking:
                if held_booking.status is BookingStatus.CANCELLED:
                    raise BookingCancellationError("Cannot cancel already cancelled booking")
                if held_booking.end_time <= self.clock():
                    raise BookingCancellationError("Cannot cancel already completed booking")
                held_booking.cancel()
                self.storage.update(held_booking)
                return
        raise BookingNotFoundError

    def _validate_request(self, request: BookingRequest) -> None:
        lot = request.lot
        spot = request.spot
        start_time = request.start_time
        end_time = request.end_time
        date_now = self.clock()

        if lot.status is not LotStatus.OPEN:
            raise LotIsNotOpenError

        if not any(available_spot is spot for available_spot in lot.available_spots):
            raise SpotOutOfServiceError

        if start_time < date_now:
            raise BookingTimeInPastError

        matched_bookings = [
            booking
            for booking in self.storage.all()
            if spot is booking.spot and booking.status is not BookingStatus.CANCELLED
        ]

        for booking in matched_bookings:
            if start_time < booking.end_time and end_time > booking.start_time:
                raise SpotAlreadyBookedError
