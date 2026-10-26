from collections.abc import Callable
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from typing import cast
from zoneinfo import ZoneInfo

import pytest

from parking_reservation.errors import (
    BookingCancellationError,
    BookingNotFoundError,
    BookingTimeInPastError,
    InvalidTimezoneError,
    LotIsNotOpenError,
    ReservationError,
    ReversedBookingTimeError,
    SpotAlreadyBookedError,
    SpotIsNotInGivenLotError,
    SpotOutOfServiceError,
)
from parking_reservation.models import (
    Location,
    LocationType,
    LotStatus,
    ParkingSpot,
    SpotStatus,
    SpotType,
)
from parking_reservation.models.booking import BookingStatus
from parking_reservation.reservation import BookingRequest, ReservationService

CLOSED_STATUSES = [status for status in LotStatus if status is not LotStatus.OPEN]


def request(lot, spot, vehicle, start_time, end_time):
    return BookingRequest(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=start_time,
        end_time=end_time,
    )


def tomorrow_at(date_tomorrow, hour, minute=0):
    return date_tomorrow.replace(hour=hour, minute=minute)


def test_reservation_error_catches_specific_error():
    with pytest.raises(ReservationError):
        raise SpotOutOfServiceError


def test_reserving_free_spot_returns_reserved_booking(vehicle, spot, date_tomorrow, make_lot):
    spot1 = spot
    spot2 = ParkingSpot(number=2, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot = make_lot(spot1, spot2)
    service = ReservationService()

    booking = service.reserve(
        request(
            lot,
            spot1,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 10),
        )
    )

    assert booking.spot is spot1
    assert service.bookings == [booking]


def test_reservation_service_does_not_accept_bookings_in_constructor(
    vehicle, spot, date_tomorrow, make_lot
):
    lot = make_lot(spot)
    first = ReservationService().reserve(
        request(
            lot,
            spot,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 10),
        )
    )

    invalid_arguments = {"bookings": [first, first]}
    constructor = cast(Callable[..., object], ReservationService)
    with pytest.raises(TypeError):
        constructor(**invalid_arguments)


def test_booking_request_cannot_be_changed_after_creation(vehicle, spot, date_tomorrow, make_lot):
    booking_request = request(
        make_lot(spot),
        spot,
        vehicle,
        tomorrow_at(date_tomorrow, 9),
        tomorrow_at(date_tomorrow, 10),
    )

    attribute_name = "start_time"
    with pytest.raises(FrozenInstanceError):
        setattr(
            booking_request,
            attribute_name,
            datetime(2027, 1, 15, 9, 0, tzinfo=ZoneInfo("Asia/Tokyo")),
        )


def test_mutating_bookings_copy_does_not_inject_overlapping_booking(
    vehicle, spot, date_tomorrow, make_lot
):
    lot = make_lot(spot)
    start_time = tomorrow_at(date_tomorrow, 9)
    end_time = tomorrow_at(date_tomorrow, 10)
    service = ReservationService()
    first = service.reserve(request(lot, spot, vehicle, start_time, end_time))
    overlapping_booking = ReservationService().reserve(
        request(lot, spot, vehicle, start_time, end_time)
    )

    service.bookings.append(overlapping_booking)

    assert service.bookings == [first]
    with pytest.raises(SpotAlreadyBookedError):
        service.reserve(request(lot, spot, vehicle, start_time, end_time))


def test_two_reservations_use_different_spots(vehicle, spot, date_tomorrow, make_lot):
    spot1 = spot
    spot2 = ParkingSpot(number=2, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot = make_lot(spot1, spot2)
    service = ReservationService()

    booking1 = service.reserve(
        request(
            lot,
            spot1,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 10),
        )
    )
    booking2 = service.reserve(
        request(
            lot,
            spot2,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 10),
        )
    )

    assert booking1.spot is spot1
    assert booking2.spot is spot2


def test_reserving_past_last_available_spot_raises_error(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot(spot)
    service = ReservationService()
    booking_request = request(
        lot,
        spot,
        vehicle,
        tomorrow_at(date_tomorrow, 9),
        tomorrow_at(date_tomorrow, 10),
    )

    service.reserve(booking_request)

    with pytest.raises(SpotAlreadyBookedError):
        service.reserve(booking_request)


def test_empty_lot_is_not_full_but_reservation_raises(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot()
    assert not lot.is_full

    service = ReservationService()
    with pytest.raises(SpotIsNotInGivenLotError):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                tomorrow_at(date_tomorrow, 9),
                tomorrow_at(date_tomorrow, 10),
            )
        )


def test_cancel_changes_booking_status(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot(spot)
    service = ReservationService()

    booking = service.reserve(
        request(
            lot,
            spot,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 10),
        )
    )
    service.cancel(booking)

    assert service.bookings[0].status is BookingStatus.CANCELLED


def test_cancelling_booking_twice_raises_on_second_attempt(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot(spot)
    service = ReservationService()

    booking = service.reserve(
        request(
            lot,
            spot,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 10),
        )
    )
    service.cancel(booking)

    with pytest.raises(BookingCancellationError, match="Cannot cancel already cancelled booking"):
        service.cancel(booking)


def test_failed_reserve_doesnt_creates_booking(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot(spot)
    service = ReservationService()

    with pytest.raises(ReversedBookingTimeError):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                tomorrow_at(date_tomorrow, 10),
                tomorrow_at(date_tomorrow, 9),
            )
        )

    assert service.bookings == []


def test_cancelling_not_owned_booking_raises(vehicle, spot, date_tomorrow, make_lot):
    spot1 = spot
    spot2 = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot1 = make_lot(spot1)
    lot2 = make_lot(spot2, number=2)
    service1 = ReservationService()
    service2 = ReservationService()

    booking1 = service1.reserve(
        request(
            lot1,
            spot1,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 10),
        )
    )
    booking2 = service2.reserve(
        request(
            lot2,
            spot2,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 10),
        )
    )

    assert booking1 is not booking2

    with pytest.raises(BookingNotFoundError):
        service1.cancel(booking2)

    assert service1.bookings == [booking1]
    assert service2.bookings == [booking2]


@pytest.mark.parametrize(
    ("requested_start", "requested_end", "overlaps"),
    [
        ((13, 0), (15, 0), False),
        ((10, 0), (12, 0), True),
        ((9, 0), (17, 0), True),
        ((9, 0), (11, 0), True),
        ((11, 0), (13, 0), False),
    ],
)
def test_booking_overlap_cases(
    vehicle,
    spot,
    requested_start,
    requested_end,
    overlaps,
    date_tomorrow,
    make_lot,
):
    lot = make_lot(spot)
    service = ReservationService()
    service.reserve(
        request(
            lot,
            spot,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 11),
        )
    )
    requested_start = tomorrow_at(date_tomorrow, *requested_start)
    requested_end = tomorrow_at(date_tomorrow, *requested_end)

    if overlaps:
        with pytest.raises(SpotAlreadyBookedError):
            service.reserve(request(lot, spot, vehicle, requested_start, requested_end))
    else:
        booking = service.reserve(request(lot, spot, vehicle, requested_start, requested_end))
        assert booking.spot is spot


def test_booking_wholly_inside_existing_booking_is_rejected(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot(spot)
    service = ReservationService()
    service.reserve(
        request(
            lot,
            spot,
            vehicle,
            tomorrow_at(date_tomorrow, 9),
            tomorrow_at(date_tomorrow, 17),
        )
    )

    with pytest.raises(SpotAlreadyBookedError):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                tomorrow_at(date_tomorrow, 10),
                tomorrow_at(date_tomorrow, 12),
            )
        )


def test_booking_containing_existing_booking_is_rejected(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot(spot)
    service = ReservationService()
    service.reserve(
        request(
            lot,
            spot,
            vehicle,
            tomorrow_at(date_tomorrow, 10),
            tomorrow_at(date_tomorrow, 12),
        )
    )

    with pytest.raises(SpotAlreadyBookedError):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                tomorrow_at(date_tomorrow, 9),
                tomorrow_at(date_tomorrow, 13),
            )
        )


def test_future_booking_does_not_block_earlier_booking_today(location, vehicle, spot, make_lot):
    lot = make_lot(spot)
    service = ReservationService()
    today_start = datetime.now(location.timezone) + timedelta(hours=1)
    future_start = today_start + timedelta(days=7)

    future_booking = service.reserve(
        request(
            lot,
            spot,
            vehicle,
            future_start,
            future_start + timedelta(hours=1),
        )
    )
    today_booking = service.reserve(
        request(
            lot,
            spot,
            vehicle,
            today_start,
            today_start + timedelta(hours=1),
        )
    )

    assert future_booking.spot is spot
    assert today_booking.spot is spot


def test_second_free_spot_is_available_when_first_spot_is_booked(
    vehicle, spot, date_tomorrow, make_lot
):
    second_spot = ParkingSpot(
        number=2,
        status=SpotStatus.AVAILABLE,
        type=SpotType.GENERAL,
    )
    lot = make_lot(spot, second_spot)
    service = ReservationService()
    start_time = tomorrow_at(date_tomorrow, 9)
    end_time = tomorrow_at(date_tomorrow, 10)

    service.reserve(request(lot, spot, vehicle, start_time, end_time))
    second_booking = service.reserve(request(lot, second_spot, vehicle, start_time, end_time))

    assert second_booking.spot is second_spot


def test_cancelling_booking_makes_its_hours_bookable_again(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot(spot)
    service = ReservationService()
    booking_request = request(
        lot,
        spot,
        vehicle,
        tomorrow_at(date_tomorrow, 9),
        tomorrow_at(date_tomorrow, 10),
    )

    booking = service.reserve(booking_request)
    service.cancel(booking)
    replacement = service.reserve(booking_request)

    assert replacement.spot is booking.spot


def test_reserving_spot_not_in_lot_is_rejected(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot(spot)
    foreign_spot = ParkingSpot(
        number=2,
        status=SpotStatus.AVAILABLE,
        type=SpotType.GENERAL,
    )
    service = ReservationService()

    with pytest.raises(SpotIsNotInGivenLotError):
        service.reserve(
            request(
                lot,
                foreign_spot,
                vehicle,
                tomorrow_at(date_tomorrow, 9),
                tomorrow_at(date_tomorrow, 10),
            )
        )


def test_reserving_out_of_service_spot_is_rejected(vehicle, spot, date_tomorrow, make_lot):
    dead_spot = ParkingSpot(
        number=2,
        status=SpotStatus.OUT_OF_SERVICE,
        type=SpotType.GENERAL,
    )
    lot = make_lot(spot, dead_spot)
    service = ReservationService()

    with pytest.raises(SpotOutOfServiceError):
        service.reserve(
            request(
                lot,
                dead_spot,
                vehicle,
                tomorrow_at(date_tomorrow, 9),
                tomorrow_at(date_tomorrow, 10),
            )
        )

    assert service.bookings == []


def test_reserving_in_the_past_is_rejected(vehicle, spot, date_tomorrow, make_lot):
    lot = make_lot(spot)
    yesterday = date_tomorrow - timedelta(days=2)
    service = ReservationService()

    with pytest.raises(BookingTimeInPastError):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                yesterday.replace(hour=9),
                yesterday.replace(hour=10),
            )
        )

    assert service.bookings == []


@pytest.mark.parametrize("closed_status", CLOSED_STATUSES)
def test_unavailable_lot_rejects_reservation(vehicle, spot, date_tomorrow, closed_status, make_lot):
    lot = make_lot(spot, status=closed_status)
    service = ReservationService()

    with pytest.raises(LotIsNotOpenError):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                tomorrow_at(date_tomorrow, 9),
                tomorrow_at(date_tomorrow, 10),
            )
        )

    assert service.bookings == []


def test_nonexistent_local_time_is_rejected(vehicle, spot, make_lot):
    oslo = ZoneInfo("Europe/Oslo")
    lot = make_lot(spot)

    with pytest.raises(InvalidTimezoneError, match="start_time is not a valid local time"):
        request(
            lot,
            spot,
            vehicle,
            datetime(2027, 3, 28, 2, 30, tzinfo=oslo),
            datetime(2027, 3, 28, 3, 30, tzinfo=oslo),
        )


def test_repeated_autumn_hour_is_distinguished_by_fold(vehicle, spot, make_lot):
    oslo = ZoneInfo("Europe/Oslo")
    lot = make_lot(spot)
    service = ReservationService()
    first_occurrence = datetime(2027, 10, 31, 2, 30, tzinfo=oslo, fold=0)
    second_occurrence = datetime(2027, 10, 31, 2, 30, tzinfo=oslo, fold=1)

    first_booking = service.reserve(
        request(
            lot,
            spot,
            vehicle,
            first_occurrence,
            datetime(2027, 10, 31, 2, 45, tzinfo=oslo, fold=0),
        )
    )
    second_booking = service.reserve(
        request(
            lot,
            spot,
            vehicle,
            second_occurrence,
            datetime(2027, 10, 31, 2, 45, tzinfo=oslo, fold=1),
        )
    )

    assert first_booking.start_time == datetime(2027, 10, 31, 0, 30, tzinfo=UTC)
    assert second_booking.start_time == datetime(2027, 10, 31, 1, 30, tzinfo=UTC)


def test_same_local_time_in_different_lot_timezones_is_different_instant(vehicle, spot, make_lot):
    oslo = ZoneInfo("Europe/Oslo")
    new_york = ZoneInfo("America/New_York")
    oslo_lot = make_lot(
        spot,
        location=Location(
            type=LocationType.RESIDENTIAL,
            address="Oslo",
            timezone=oslo,
        ),
    )
    new_york_lot = make_lot(
        spot,
        number=2,
        location=Location(
            type=LocationType.RESIDENTIAL,
            address="New York",
            timezone=new_york,
        ),
    )

    oslo_request = request(
        oslo_lot,
        spot,
        vehicle,
        datetime(2027, 1, 15, 9, 0, tzinfo=oslo),
        datetime(2027, 1, 15, 10, 0, tzinfo=oslo),
    )
    new_york_request = request(
        new_york_lot,
        spot,
        vehicle,
        datetime(2027, 1, 15, 9, 0, tzinfo=new_york),
        datetime(2027, 1, 15, 10, 0, tzinfo=new_york),
    )

    assert oslo_request.start_time == datetime(2027, 1, 15, 8, 0, tzinfo=UTC)
    assert new_york_request.start_time == datetime(2027, 1, 15, 14, 0, tzinfo=UTC)


def test_booking_request_rejects_start_time_not_in_lot_timezone(location, vehicle, spot, make_lot):
    lot = make_lot(spot)
    with pytest.raises(InvalidTimezoneError, match="start_time must use the lot's timezone"):
        BookingRequest(
            lot=lot,
            spot=spot,
            vehicle=vehicle,
            start_time=datetime(2027, 1, 15, 9, 0, tzinfo=ZoneInfo("America/New_York")),
            end_time=datetime(2027, 1, 15, 10, 0, tzinfo=location.timezone),
        )


def test_completed_booking_cannot_be_cancelled(make_lot, location, vehicle, spot):
    lot = make_lot(spot)
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    service = ReservationService(clock=lambda: now)
    start = datetime(2027, 3, 1, 10, 0, tzinfo=location.timezone)
    booking = service.reserve(request(lot, spot, vehicle, start, start + timedelta(hours=1)))

    now = datetime(2027, 3, 2, 8, 0, tzinfo=UTC)

    with pytest.raises(BookingCancellationError, match="Cannot cancel already completed booking"):
        service.cancel(booking)


def test_active_booking_can_be_cancelled_and_remains_in_service(make_lot, location, vehicle, spot):
    lot = make_lot(spot)
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    service = ReservationService(clock=lambda: now)
    start = datetime(2027, 3, 1, 10, 0, tzinfo=location.timezone)
    booking = service.reserve(request(lot, spot, vehicle, start, start + timedelta(hours=1)))
    original_total = booking.total

    now = datetime(2027, 3, 1, 10, 30, tzinfo=location.timezone)
    service.cancel(booking)

    assert booking.status is BookingStatus.CANCELLED
    assert service.bookings == [booking]
    assert booking.total == original_total


def test_cancelled_active_booking_remaining_time_is_bookable(make_lot, location, vehicle, spot):
    lot = make_lot(spot)
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    service = ReservationService(clock=lambda: now)
    start = datetime(2027, 3, 1, 10, 0, tzinfo=location.timezone)
    end = start + timedelta(hours=1)
    booking = service.reserve(request(lot, spot, vehicle, start, end))

    now = datetime(2027, 3, 1, 10, 30, tzinfo=location.timezone)
    service.cancel(booking)
    service.reserve(request(lot, spot, vehicle, now, end))
