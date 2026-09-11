from parking_reservation.models.enums import (
    LocationType,
    LotStatus,
    LotType,
    SpotStatus,
    SpotType,
)
from parking_reservation.models.location import Location
from parking_reservation.models.parking_lot import ParkingLot
from parking_reservation.models.parking_spot import ParkingSpot


def test_newly_built_lot_has_empty_spots_list():
    location = Location(type=LocationType.RESIDENTIAL, address="Oslo")
    lot = ParkingLot(number=1, status=LotStatus.OPEN, type=LotType.PUBLIC, location=location)
    assert lot.spots == []


def test_lots_dont_share_spots():
    spot = ParkingSpot(number=1, status=SpotStatus.OCCUPIED, type=SpotType.MANAGEMENT)

    location1 = Location(type=LocationType.RESIDENTIAL, address="Oslo")
    location2 = Location(type=LocationType.RESIDENTIAL, address="Lviv")
    lot1 = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location1,
        spots=[spot],
    )

    lot2 = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location2,
    )

    assert lot1.spots == [spot]
    assert lot2.spots == []


def test_lots_save_spots_with_right_count():
    spot1 = ParkingSpot(number=1, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    spot2 = ParkingSpot(number=2, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)
    spot3 = ParkingSpot(number=3, status=SpotStatus.AVAILABLE, type=SpotType.GENERAL)

    location = Location(type=LocationType.RESIDENTIAL, address="Paris")
    lot = ParkingLot(
        number=1,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1, spot2, spot3],
    )

    assert len(lot.spots) == 3
