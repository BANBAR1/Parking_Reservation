from datetime import datetime

import pytest

from parking_reservation.models.booking import Booking
from parking_reservation.models.enums import SpotStatus, SpotType
from parking_reservation.models.parking_spot import ParkingSpot


def test_total_cost_for_a_general_spot(vehicle):
    spot = ParkingSpot(number=12, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)

    booking = Booking(
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 12, 30),
    )

    assert booking.duration_hours() == 3.5
    assert booking.total_cost() == pytest.approx(8.75)


def test_booking_rejects_backwards_time_range(vehicle):
    spot = ParkingSpot(number=12, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)

    with pytest.raises(ValueError, match="end_time"):
        Booking(
            spot=spot,
            vehicle=vehicle,
            start_time=datetime(2026, 9, 1, 12, 0),
            end_time=datetime(2026, 9, 1, 9, 0),
        )


@pytest.mark.parametrize(
    "spot_type, expected_cost",
    [
        (SpotType.GENERAL, 5.00),
        (SpotType.DISABLED, 2.00),
        (SpotType.ELECTRIC_VEHICLES, 7.00),
        (SpotType.WORKERS, 0.00),
    ],
)
def test_cost_follows_the_spot_type(vehicle, spot_type, expected_cost):
    spot = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=spot_type)

    booking = Booking(
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 11, 0),
    )

    assert booking.total_cost() == pytest.approx(expected_cost)


def test_short_stay_on_an_ev_spot(vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.ELECTRIC_VEHICLES)
    booking = Booking(
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 9, 12),
    )

    assert booking.total_cost() == pytest.approx(0.70)
