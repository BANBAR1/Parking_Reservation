import pytest

from parking_reservation.models import (
    Driver,
    Location,
    LocationType,
    ParkingSpot,
    SpotStatus,
    SpotType,
    Vehicle,
)


@pytest.fixture
def vehicle():
    return Vehicle(license_plate="WZ12345", driver=Driver(name="Andrii"))


@pytest.fixture
def location():
    return Location(type=LocationType.RESIDENTIAL, address="Oslo")


@pytest.fixture
def spot():
    return ParkingSpot(
        number=1,
        status=SpotStatus.AVAILABLE,
        type=SpotType.GENERAL,
    )
