from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from parking_reservation.errors import (
    BookingNotFoundError,
    BookingTimeInPastError,
    LotIsNotOpenError,
    SpotAlreadyBookedError,
    SpotOutOfServiceError,
)
from parking_reservation.models import Booking, LotStatus, ParkingLot, ParkingSpot, Vehicle
from parking_reservation.models.booking import BookingStatus
from parking_reservation.pricing import rate_for, rule_for
from parking_reservation.timekeeping import as_utc_from


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
    _bookings: list[Booking] = field(default_factory=list[Booking], init=False)
    clock: Callable[[], datetime] = lambda: datetime.now(UTC)

    @property
    def bookings(self) -> list[Booking]:
        return self._bookings.copy()

    def reserve(self, request: BookingRequest) -> Booking:
        lot = request.lot
        spot = request.spot
        vehicle = request.vehicle
        start_time = request.start_time
        end_time = request.end_time

        booking = Booking(
            lot=lot,
            spot=spot,
            vehicle=vehicle,
            start_time=start_time,
            end_time=end_time,
            hourly_rate=rate_for(spot.type),
            pricing_rule=rule_for(spot.type),
        )

        self._validate_request(request)
        self._bookings.append(booking)

        return booking

    def cancel(self, booking: Booking) -> None:
        for held_booking in self._bookings:
            if held_booking is booking:
                held_booking.cancel(self.clock())
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
            for booking in self._bookings
            if spot is booking.spot and booking.status(date_now) != BookingStatus.CANCELLED
        ]

        for booking in matched_bookings:
            if start_time < booking.end_time and end_time > booking.start_time:
                raise SpotAlreadyBookedError
