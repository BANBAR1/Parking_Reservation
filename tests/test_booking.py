from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from parking_reservation.errors import TimezoneError
from parking_reservation.models import (
    Booking,
    LotStatus,
    LotType,
    ParkingLot,
    ParkingSpot,
    SpotStatus,
    SpotType,
)


def make_lot(location, spot):
    return ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )


def test_total_cost_for_a_general_spot(location, vehicle):
    spot = ParkingSpot(number=12, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)

    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 1, 12, 30, tzinfo=location.timezone),
    )

    assert booking.duration_hours() == 3.5
    assert booking.total_cost() == pytest.approx(8.75)


@pytest.mark.parametrize(
    "spot_type, expected_cost",
    [
        (SpotType.GENERAL, 5.00),
        (SpotType.DISABLED, 2.00),
        (SpotType.ELECTRIC_VEHICLES, 7.00),
        (SpotType.WORKERS, 0.00),
    ],
)
def test_cost_follows_the_spot_type(location, vehicle, spot_type, expected_cost):
    spot = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=spot_type)

    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 1, 11, 0, tzinfo=location.timezone),
    )

    assert booking.total_cost() == pytest.approx(expected_cost)


def test_short_stay_on_an_ev_spot(location, vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.ELECTRIC_VEHICLES)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 1, 9, 12, tzinfo=location.timezone),
    )

    assert booking.total_cost() == pytest.approx(0.70)


def test_duration_counts_elapsed_time_across_spring_forward(location, vehicle):
    oslo = ZoneInfo("Europe/Oslo")
    spot = ParkingSpot(number=12, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2027, 3, 28, 1, 30, tzinfo=oslo),
        end_time=datetime(2027, 3, 28, 3, 30, tzinfo=oslo),
    )

    assert booking.duration_hours() == 1
    assert booking.total_cost() == pytest.approx(2.50)


def test_direct_booking_rejects_naive_start_time(location, vehicle):
    spot = ParkingSpot(number=12, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    with pytest.raises(TimezoneError, match="start_time must be timezone-aware"):
        Booking(
            lot=make_lot(location, spot),
            spot=spot,
            vehicle=vehicle,
            start_time=datetime(2027, 5, 1, 9, 0),
            end_time=datetime(2027, 5, 1, 10, 0),
        )
