from datetime import datetime, timedelta

import pytest

from parking_reservation.models import (
    LotStatus,
    LotType,
    ParkingLot,
    ParkingSpot,
    SpotStatus,
    SpotType,
)
from parking_reservation.reservation import BookingRequest, ReservationService


def request(lot, spot, vehicle, start_time, end_time):
    return BookingRequest(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=start_time,
        end_time=end_time,
    )


def test_reserving_free_spot_returns_reserved_booking(location, vehicle, spot):
    spot1 = spot
    spot2 = ParkingSpot(number=2, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1, spot2],
    )
    service = ReservationService()

    booking = service.reserve(
        request(
            lot,
            spot1,
            vehicle,
            datetime(2026, 9, 20, 9, 0),
            datetime(2026, 9, 20, 10, 0),
        )
    )

    assert booking.spot is spot1
    assert service.bookings == [booking]


def test_two_reservations_use_different_spots(location, vehicle, spot):
    spot1 = spot
    spot2 = ParkingSpot(number=2, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1, spot2],
    )
    service = ReservationService()

    booking1 = service.reserve(
        request(
            lot,
            spot1,
            vehicle,
            datetime(2026, 9, 20, 9, 0),
            datetime(2026, 9, 20, 10, 0),
        )
    )
    booking2 = service.reserve(
        request(
            lot,
            spot2,
            vehicle,
            datetime(2026, 9, 20, 9, 0),
            datetime(2026, 9, 20, 10, 0),
        )
    )

    assert booking1.spot is spot1
    assert booking2.spot is spot2


def test_reserving_past_last_available_spot_raises_error(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()
    booking_request = request(
        lot,
        spot,
        vehicle,
        datetime(2026, 9, 20, 9, 0),
        datetime(2026, 9, 20, 10, 0),
    )

    service.reserve(booking_request)

    with pytest.raises(ValueError, match="Request is not valid"):
        service.reserve(booking_request)


def test_empty_lot_is_not_full_but_reservation_raises(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
    )
    assert not lot.is_full

    service = ReservationService()
    with pytest.raises(ValueError, match="Request is not valid"):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                datetime(2026, 9, 20, 9, 0),
                datetime(2026, 9, 20, 10, 0),
            )
        )


def test_cancel_removes_booking(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()

    booking = service.reserve(
        request(
            lot,
            spot,
            vehicle,
            datetime(2026, 9, 20, 9, 0),
            datetime(2026, 9, 20, 10, 0),
        )
    )
    service.cancel(booking)

    assert service.bookings == []


def test_cancelling_booking_allows_reservation_again(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()
    booking_request = request(
        lot,
        spot,
        vehicle,
        datetime(2026, 9, 20, 9, 0),
        datetime(2026, 9, 20, 10, 0),
    )

    first_booking = service.reserve(booking_request)
    service.cancel(first_booking)
    new_booking = service.reserve(booking_request)

    assert new_booking.spot is spot


def test_cancelling_booking_twice_raises_on_second_attempt(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()

    booking = service.reserve(
        request(
            lot,
            spot,
            vehicle,
            datetime(2026, 9, 20, 9, 0),
            datetime(2026, 9, 20, 10, 0),
        )
    )
    service.cancel(booking)

    with pytest.raises(ValueError, match="Booking was not found"):
        service.cancel(booking)


def test_failed_reserve_doesnt_creates_booking(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()

    with pytest.raises(ValueError, match="Request is not valid"):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                datetime(2026, 9, 20, 10, 0),
                datetime(2026, 9, 20, 9, 0),
            )
        )

    assert service.bookings == []


def test_cancelling_not_owned_booking_raises(location, vehicle, spot):
    spot1 = spot
    spot2 = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot1 = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1],
    )
    lot2 = ParkingLot(
        number=2,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot2],
    )
    service1 = ReservationService()
    service2 = ReservationService()

    booking1 = service1.reserve(
        request(
            lot1,
            spot1,
            vehicle,
            datetime(2026, 9, 20, 9, 0),
            datetime(2026, 9, 20, 10, 0),
        )
    )
    booking2 = service2.reserve(
        request(
            lot2,
            spot2,
            vehicle,
            datetime(2026, 9, 20, 9, 0),
            datetime(2026, 9, 20, 10, 0),
        )
    )

    assert booking1 is not booking2

    with pytest.raises(ValueError, match="Booking was not found"):
        service1.cancel(booking2)

    assert service1.bookings == [booking1]
    assert service2.bookings == [booking2]


@pytest.mark.parametrize(
    ("requested_start", "requested_end", "overlaps"),
    [
        (datetime(2026, 9, 20, 13, 0), datetime(2026, 9, 20, 15, 0), False),
        (datetime(2026, 9, 20, 10, 0), datetime(2026, 9, 20, 12, 0), True),
        (datetime(2026, 9, 20, 10, 0), datetime(2026, 9, 20, 12, 0), True),
        (datetime(2026, 9, 20, 9, 0), datetime(2026, 9, 20, 17, 0), True),
        (datetime(2026, 9, 20, 9, 0), datetime(2026, 9, 20, 11, 0), True),
        (datetime(2026, 9, 20, 11, 0), datetime(2026, 9, 20, 13, 0), False),
    ],
)
def test_booking_overlap_cases(
    location,
    vehicle,
    spot,
    requested_start,
    requested_end,
    overlaps,
):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()
    service.reserve(
        request(
            lot,
            spot,
            vehicle,
            datetime(2026, 9, 20, 9, 0),
            datetime(2026, 9, 20, 11, 0),
        )
    )

    if overlaps:
        with pytest.raises(ValueError, match="Request is not valid"):
            service.reserve(request(lot, spot, vehicle, requested_start, requested_end))
    else:
        booking = service.reserve(request(lot, spot, vehicle, requested_start, requested_end))
        assert booking.spot is spot


def test_booking_wholly_inside_existing_booking_is_rejected(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()
    service.reserve(
        request(
            lot,
            spot,
            vehicle,
            datetime(2026, 9, 20, 9, 0),
            datetime(2026, 9, 20, 17, 0),
        )
    )

    with pytest.raises(ValueError, match="Request is not valid"):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                datetime(2026, 9, 20, 10, 0),
                datetime(2026, 9, 20, 12, 0),
            )
        )


def test_booking_containing_existing_booking_is_rejected(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()
    service.reserve(
        request(
            lot,
            spot,
            vehicle,
            datetime(2026, 9, 20, 10, 0),
            datetime(2026, 9, 20, 12, 0),
        )
    )

    with pytest.raises(ValueError, match="Request is not valid"):
        service.reserve(
            request(
                lot,
                spot,
                vehicle,
                datetime(2026, 9, 20, 9, 0),
                datetime(2026, 9, 20, 13, 0),
            )
        )


def test_future_booking_does_not_block_earlier_booking_today(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()
    today_start = datetime.now() + timedelta(hours=1)
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


def test_second_free_spot_is_available_when_first_spot_is_booked(location, vehicle, spot):
    second_spot = ParkingSpot(
        number=2,
        status=SpotStatus.AVAILABLE,
        type=SpotType.GENERAL,
    )
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot, second_spot],
    )
    service = ReservationService()
    start_time = datetime(2026, 9, 20, 9, 0)
    end_time = datetime(2026, 9, 20, 10, 0)

    service.reserve(request(lot, spot, vehicle, start_time, end_time))
    second_booking = service.reserve(request(lot, second_spot, vehicle, start_time, end_time))

    assert second_booking.spot is second_spot


def test_cancelling_booking_makes_its_hours_bookable_again(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()
    booking_request = request(
        lot,
        spot,
        vehicle,
        datetime(2026, 9, 20, 9, 0),
        datetime(2026, 9, 20, 10, 0),
    )

    booking = service.reserve(booking_request)
    service.cancel(booking)
    replacement = service.reserve(booking_request)

    assert replacement.spot is booking.spot


def test_reserving_spot_not_in_lot_is_rejected(location, vehicle, spot):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    foreign_spot = ParkingSpot(
        number=2,
        status=SpotStatus.AVAILABLE,
        type=SpotType.GENERAL,
    )
    service = ReservationService()

    with pytest.raises(ValueError, match="Request is not valid"):
        service.reserve(
            request(
                lot,
                foreign_spot,
                vehicle,
                datetime(2026, 9, 20, 9, 0),
                datetime(2026, 9, 20, 10, 0),
            )
        )
