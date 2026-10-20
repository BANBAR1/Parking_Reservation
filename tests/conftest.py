from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

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
def date_tomorrow():
    return datetime.now(OSLO).replace(minute=0, second=0, microsecond=0) + timedelta(days=1)


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
