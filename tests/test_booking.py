from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from parking_reservation.errors import InvalidTimezoneError
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

    assert booking.duration_hours() == Decimal("3.50")
    assert booking.total_cost() == Decimal("8.75")


@pytest.mark.parametrize(
    "spot_type, expected_cost",
    [
        (SpotType.GENERAL, Decimal("5.00")),
        (SpotType.DISABLED, Decimal("2.00")),
        (SpotType.ELECTRIC_VEHICLES, Decimal("7.00")),
        (SpotType.MANAGEMENT, Decimal("0.00")),
        (SpotType.WORKERS, Decimal("0.00")),
        (SpotType.VISITORS, Decimal("0.00")),
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

    assert booking.total_cost() == expected_cost


def test_short_stay_on_an_ev_spot(location, vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.ELECTRIC_VEHICLES)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 1, 9, 12, tzinfo=location.timezone),
    )

    assert booking.total_cost() == Decimal("0.70")


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

    assert booking.duration_hours() == Decimal("1.00")
    assert booking.total_cost() == Decimal("2.50")


def test_direct_booking_rejects_naive_start_time(location, vehicle):
    spot = ParkingSpot(number=12, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    with pytest.raises(InvalidTimezoneError, match="start_time must be timezone-aware"):
        Booking(
            lot=make_lot(location, spot),
            spot=spot,
            vehicle=vehicle,
            start_time=datetime(2027, 5, 1, 9, 0),
            end_time=datetime(2027, 5, 1, 10, 0),
        )


def test_booking_cost_rounds_up(location, vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 1, 9, 13, tzinfo=location.timezone),
    )

    assert booking.total_cost() == Decimal("0.55")


def test_daily_cap_pricing_under_cap_is_correct(location, vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 20, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 1, 11, 20, tzinfo=location.timezone),
    )

    assert booking.total_cost() == Decimal("5")


def test_daily_cap_pricing_at_cap_charges_once(location, vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 20, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 1, 15, 20, tzinfo=location.timezone),
    )

    assert booking.total_cost() == Decimal("15")


def test_daily_cap_pricing_just_past_cap_charges_the_cap(location, vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 20, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 1, 15, 21, tzinfo=location.timezone),
    )

    assert booking.total_cost() == Decimal("15.00")


def test_daily_cap_pricing_over_cap_limits_charge(location, vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 20, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 2, 6, 20, tzinfo=location.timezone),
    )

    assert booking.total_cost() == Decimal("15")


def test_daily_cap_pricing_over_cap_includes_over_24_hours(location, vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 20, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 3, 12, 20, tzinfo=location.timezone),
    )

    assert booking.total_cost() == Decimal("37.5")


def test_same_duration_bookings_at_different_rates_have_exact_cost_difference(location, vehicle):
    spot1 = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    booking1 = Booking(
        lot=make_lot(location, spot1),
        spot=spot1,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 20, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 3, 12, 20, tzinfo=location.timezone),
    )

    spot2 = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.DISABLED)
    booking2 = Booking(
        lot=make_lot(location, spot2),
        spot=spot2,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 20, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 3, 12, 20, tzinfo=location.timezone),
    )

    assert booking1.total_cost() - booking2.total_cost() == Decimal("4.50")


def test_duration_is_not_rounded(location, vehicle):
    spot = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    booking = Booking(
        lot=make_lot(location, spot),
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0, tzinfo=location.timezone),
        end_time=datetime(2026, 9, 1, 9, 20, tzinfo=location.timezone),
    )

    assert booking.duration_hours() == Decimal(1) / 3
