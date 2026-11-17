from datetime import UTC, datetime, timedelta
from decimal import Decimal

import psycopg
import pytest

from parking_reservation.booking_database import BookingDatabase
from parking_reservation.errors import SpotAlreadyBookedError
from parking_reservation.models import (
    Booking,
    BookingStatus,
    Driver,
    LotCollection,
    Vehicle,
)
from parking_reservation.reservation import (
    BookingRequest,
    ReservationService,
)

NOW = datetime(2026, 1, 1, tzinfo=UTC)
BOOKING_START = datetime(2027, 3, 2, 8, tzinfo=UTC)


@pytest.fixture(autouse=True)
def drop_bookings_table(connection):
    connection.execute("DROP TABLE IF EXISTS bookings")


@pytest.fixture
def lots(make_lot, spot):
    lot = make_lot(spot, number=32)
    collection = LotCollection()
    collection.add(lot)
    return collection


@pytest.fixture
def make_storage(database_url):
    def create(lots):
        return BookingDatabase(database_url, lots)

    return create


def make_request(lot, spot, vehicle, start=BOOKING_START):
    return BookingRequest(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=start.astimezone(lot.location.timezone),
        end_time=(start + timedelta(hours=2)).astimezone(lot.location.timezone),
    )


def make_service(storage):
    return ReservationService(storage=storage, clock=lambda: NOW)


def test_database_answers(connection):
    assert connection.execute("SELECT 1").fetchone() == (1,)


def test_new_database_has_no_bookings(make_storage, lots):
    storage = make_storage(lots)

    assert storage.all() == []


def test_reserved_booking_round_trips_through_another_storage(make_storage, lots, vehicle, spot):
    lot = lots.get(32)
    booking = make_service(make_storage(lots)).reserve(make_request(lot, spot, vehicle))

    restored = make_storage(lots).all()[0]

    assert vars(restored) == vars(booking)


def test_money_keeps_two_decimal_places(make_storage, lots, vehicle, spot):
    lot = lots.get(32)
    booking = Booking(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=BOOKING_START,
        end_time=BOOKING_START + timedelta(hours=2),
        hourly_rate=Decimal("2.50"),
        total=Decimal("5.00"),
    )
    storage = make_storage(lots)
    storage.add(booking)

    restored = make_storage(lots).all()[0]

    assert str(restored.total) == "5.00"


def test_cancelling_one_booking_only_updates_that_booking(make_storage, lots, vehicle, spot):
    service = make_service(make_storage(lots))
    lot = lots.get(32)
    first = service.reserve(make_request(lot, spot, vehicle))
    second = service.reserve(
        make_request(lot, spot, vehicle, start=BOOKING_START + timedelta(days=1))
    )

    service.cancel(first)

    restored = make_storage(lots).all()
    statuses = {booking.id: booking.status for booking in restored}
    assert statuses == {
        first.id: BookingStatus.CANCELLED,
        second.id: BookingStatus.ACTIVE,
    }


def test_second_app_sees_and_rejects_an_existing_booking(make_storage, lots, vehicle, spot):
    lot = lots.get(32)
    first_service = make_service(make_storage(lots))
    second_service = make_service(make_storage(lots))
    first_service.reserve(make_request(lot, spot, vehicle))

    with pytest.raises(SpotAlreadyBookedError):
        second_service.reserve(make_request(lot, spot, vehicle))


@pytest.mark.parametrize(
    ("driver_name", "license_plate"),
    [
        ("O'Brien", "AA1111"),
        ("Ann", "AA1', 'Ann', 5.00"),
    ],
)
def test_text_values_are_saved_exactly(
    make_storage, lots, vehicle, spot, driver_name, license_plate
):
    lot = lots.get(32)
    special_vehicle = Vehicle(
        license_plate=license_plate,
        driver=Driver(name=driver_name),
    )
    make_service(make_storage(lots)).reserve(make_request(lot, spot, special_vehicle))

    restored = make_storage(lots).all()[0]

    assert restored.vehicle.driver.name == driver_name
    assert restored.vehicle.license_plate == license_plate


def test_adding_the_same_booking_twice_is_rejected(make_storage, lots, vehicle, spot):
    lot = lots.get(32)
    booking = make_service(make_storage(lots)).reserve(make_request(lot, spot, vehicle))
    storage = make_storage(lots)

    with pytest.raises(psycopg.errors.UniqueViolation):
        storage.add(booking)

    assert len(storage.all()) == 1
