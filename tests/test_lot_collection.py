from pathlib import Path

import pytest

from parking_reservation.errors import DuplicateLotNumberError, LotNotFoundError
from parking_reservation.models import (
    Location,
    LocationType,
    LotCollection,
    LotStatus,
    LotType,
    ParkingLot,
)
from parking_reservation.utilities import lot_loader


def test_lot_collection_saves_lots():
    collection = LotCollection()
    path = Path(__file__).parent / "fixtures" / "valid_lots.json"
    lots = lot_loader.load(path)
    for lot in lots:
        collection.add(lot)
    assert len(lots) == 5
    for lot in lots:
        assert collection.get(lot.number) == lot


def test_getting_lot_by_absent_lot_number_raises_error():
    collection = LotCollection()
    lot = ParkingLot(
        number=9,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=Location(type=LocationType.RESIDENTIAL, address="Washington"),
    )

    collection.add(lot)

    with pytest.raises(
        LotNotFoundError, match="Lot with number 8 does not exist in this collection"
    ):
        collection.get(8)


def test_adding_duplicate_lot_raises_error():
    collection = LotCollection()
    lot = ParkingLot(
        number=8,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=Location(type=LocationType.RESIDENTIAL, address="Washington"),
    )
    duplicate_lot = ParkingLot(
        number=8,
        status=LotStatus.CLOSED,
        type=LotType.PRIVATE,
        location=Location(type=LocationType.AIRPORT, address="Seattle"),
    )
    collection.add(lot)

    with pytest.raises(
        DuplicateLotNumberError,
        match="Lot with number: 8 already exists in this collection",
    ):
        collection.add(duplicate_lot)
