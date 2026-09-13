import pytest

from parking_reservation.models import (
    Location,
    LocationType,
    LotStatus,
    LotType,
    ParkingLot,
    ParkingSpot,
    SpotStatus,
    SpotType,
)


@pytest.fixture
def location():
    return Location(type=LocationType.RESIDENTIAL, address="Oslo")


def test_newly_built_lot_has_empty_spots_list(location):
    lot = ParkingLot(number=1, status=LotStatus.OPEN, type=LotType.PUBLIC, location=location)
    assert lot.spots == []


def test_lot_keeps_the_spots_it_was_built_with(location):
    spot = ParkingSpot(number=1, status=SpotStatus.OCCUPIED, type=SpotType.MANAGEMENT)

    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )

    assert lot.spots == [spot]


def test_lots_save_spots_with_right_count(location):
    spot1 = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    spot2 = ParkingSpot(number=2, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    spot3 = ParkingSpot(number=3, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)

    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1, spot2, spot3],
    )

    assert len(lot.spots) == 3


def test_lots_dont_share_spots(location):
    lot1 = ParkingLot(number=1, status=LotStatus.OPEN, type=LotType.PUBLIC, location=location)
    lot2 = ParkingLot(number=2, status=LotStatus.OPEN, type=LotType.PUBLIC, location=location)

    lot1.spots.append(ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL))

    assert lot2.spots == []


def test_lot_with_available_and_occupied_spots_is_not_full(location):
    spot1 = ParkingSpot(number=1, status=SpotStatus.OCCUPIED, type=SpotType.GENERAL)
    spot2 = ParkingSpot(number=2, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)

    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1, spot2],
    )

    assert not lot.is_full
    assert lot.available_spots == [spot2]


def test_lot_with_occupied_spots_is_full(location):
    spot1 = ParkingSpot(number=1, status=SpotStatus.OCCUPIED, type=SpotType.GENERAL)
    spot2 = ParkingSpot(number=2, status=SpotStatus.OCCUPIED, type=SpotType.GENERAL)

    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1, spot2],
    )

    assert lot.is_full
    assert lot.available_spots == []


def test_empty_lot_is_not_full(location):
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
    )

    assert not lot.is_full


def test_lot_full_state_flips(location):
    spot1 = ParkingSpot(number=1, status=SpotStatus.OCCUPIED, type=SpotType.GENERAL)
    spot2 = ParkingSpot(number=2, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)

    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1, spot2],
    )

    assert not lot.is_full

    spot2.status = SpotStatus.OCCUPIED

    assert lot.is_full


@pytest.mark.parametrize(
    "status",
    [SpotStatus.RESERVED, SpotStatus.OUT_OF_SERVICE],
)
def test_non_available_spot_counts_toward_full(status, location):
    spot = ParkingSpot(number=1, status=status, type=SpotType.GENERAL)
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot],
    )

    assert lot.available_spots == []
    assert lot.is_full
