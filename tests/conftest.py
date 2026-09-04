import pytest

from parking_reservation.models.driver import Driver
from parking_reservation.models.vehicle import Vehicle


@pytest.fixture
def vehicle():
    return Vehicle(license_plate="WZ12345", driver=Driver(name="Andrii"))
