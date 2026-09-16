from datetime import datetime

import pytest

from parking_reservation.models import (
    LotStatus,
    LotType,
    ParkingLot,
    ParkingSpot,
    SpotStatus,
    SpotType,
)
from parking_reservation.reservation import ReservationService


def test_reserving_free_spot_returns_reserved_booking(location, vehicle):
    spot1 = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
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
        lot=lot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )

    assert booking.spot is spot1
    assert booking.spot.status is SpotStatus.RESERVED
    assert service.bookings == [booking]


def test_two_reservations_use_different_spots(location, vehicle):
    spot1 = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
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
        lot=lot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )
    booking2 = service.reserve(
        lot=lot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )

    assert booking1.spot is spot1
    assert booking2.spot is spot2
    assert booking1.spot is not booking2.spot


def test_reserving_past_last_available_spot_raises_error(location, vehicle):
    spot = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()

    service.reserve(
        lot=lot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )

    with pytest.raises(ValueError, match="lot number: 1"):
        service.reserve(
            lot=lot,
            vehicle=vehicle,
            start_time=datetime(2026, 9, 1, 9, 0),
            end_time=datetime(2026, 9, 1, 10, 0),
        )


def test_empty_lot_is_not_full_but_reservation_raises(location, vehicle):

    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
    )

    assert not lot.is_full

    service = ReservationService()
    with pytest.raises(ValueError, match="lot number: 1"):
        service.reserve(
            lot=lot,
            vehicle=vehicle,
            start_time=datetime(2026, 9, 1, 9, 0),
            end_time=datetime(2026, 9, 1, 10, 0),
        )


def test_cancel_frees_spot_and_removes_booking(location, vehicle):

    spot = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()

    booking = service.reserve(
        lot=lot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )
    service.cancel(booking)

    assert spot.status is SpotStatus.AVAILABLE
    assert service.bookings == []


def test_cancelling_booking_allows_reservation_again(location, vehicle):
    spot = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()

    first_booking = service.reserve(
        lot=lot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )
    with pytest.raises(ValueError, match="lot number: 1"):
        service.reserve(
            lot=lot,
            vehicle=vehicle,
            start_time=datetime(2026, 9, 1, 9, 0),
            end_time=datetime(2026, 9, 1, 10, 0),
        )

    service.cancel(first_booking)

    new_booking = service.reserve(
        lot=lot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )

    assert new_booking.spot is spot
    assert spot.status is SpotStatus.RESERVED


def test_cancelling_booking_twice_raises_on_second_attempt(location, vehicle):

    spot = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()

    booking = service.reserve(
        lot=lot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )
    service.cancel(booking)
    with pytest.raises(ValueError, match="Booking for spot 1"):
        service.cancel(booking)


def test_failed_reserve_leaves_the_lot_untouched(location, vehicle):

    spot = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )
    service = ReservationService()
    with pytest.raises(ValueError, match="end_time must be after start_time"):
        service.reserve(
            lot=lot,
            vehicle=vehicle,
            start_time=datetime(2026, 9, 1, 10, 0),
            end_time=datetime(2026, 9, 1, 9, 0),
        )
    assert spot.status is SpotStatus.AVAILABLE
    assert service.bookings == []


def test_cancelling_equal_but_different_booking_raises(location, vehicle):
    spot1 = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
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
        lot=lot1,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )
    booking2 = service2.reserve(
        lot=lot2,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 10, 0),
    )

    assert booking1 == booking2
    assert booking1 is not booking2

    with pytest.raises(ValueError):
        service1.cancel(booking2)

    assert spot1.status is SpotStatus.RESERVED
    assert service1.bookings == [booking1]
    assert spot2.status is SpotStatus.RESERVED
    assert service2.bookings == [booking2]
