from zoneinfo import ZoneInfo

import psycopg
import pytest
from testcontainers.community.postgres import PostgresContainer

from parking_reservation.models import (
    Driver,
    Location,
    LocationType,
    LotStatus,
    LotType,
    ParkingLot,
    ParkingSpot,
    SpotStatus,
    SpotType,
    Vehicle,
)

OSLO = ZoneInfo("Europe/Oslo")


@pytest.fixture
def vehicle():
    return Vehicle(license_plate="WZ12345", driver=Driver(name="Andrii"))


@pytest.fixture
def location():
    return Location(type=LocationType.RESIDENTIAL, address="Oslo", timezone=OSLO)


@pytest.fixture
def spot():
    return ParkingSpot(
        number=1,
        status=SpotStatus.AVAILABLE,
        type=SpotType.GENERAL,
    )


@pytest.fixture
def make_lot(request):
    default_location = request.getfixturevalue("location")

    def make(*spots, number=1, status=LotStatus.OPEN, location=None):
        return ParkingLot(
            number=number,
            status=status,
            type=LotType.PUBLIC,
            location=location if location is not None else default_location,
            spots=list(spots),
        )

    return make


@pytest.fixture(scope="session")
def database_url():
    with PostgresContainer("postgres:18.6", driver=None) as postgres:
        yield postgres.get_connection_url()


@pytest.fixture
def connection(database_url):
    with psycopg.connect(database_url, autocommit=True, connect_timeout=5) as connection:
        yield connection
