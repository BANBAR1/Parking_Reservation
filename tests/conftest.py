import pytest

from parking_reservation.models import Driver, Vehicle


@pytest.fixture
def vehicle():
    return Vehicle(license_plate="WZ12345", driver=Driver(name="Andrii"))
