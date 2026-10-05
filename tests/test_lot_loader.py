from pathlib import Path

import pytest

from parking_reservation.errors import (
    DuplicateSpotNumberError,
    InvalidEnumError,
    KeyMissingError,
    LotDescriptionKeyTypeError,
)
from parking_reservation.models import (
    Location,
    LocationType,
    LotStatus,
    LotType,
    SpotStatus,
    SpotType,
)
from parking_reservation.utilities import lot_loader


def test_loads_lot_from_json_right():
    path = Path(__file__).parent / "fixtures" / "valid_lot.json"
    lot = lot_loader.load(path)

    assert lot.number == 32
    assert lot.location == Location(type=LocationType.RESIDENTIAL, address="Washington")
    assert len(lot.spots) == 3
    assert lot.spots[0].number == 3
    assert lot.spots[1].number == 5
    assert lot.spots[2].number == 6


def test_load_lot_converts_enum_fields():
    path = Path(__file__).parent / "fixtures" / "valid_lot.json"
    lot = lot_loader.load(path)

    assert lot.status is LotStatus.OPEN
    assert lot.type is LotType.PUBLIC
    assert lot.location.type is LocationType.RESIDENTIAL
    assert lot.spots[0].status is SpotStatus.AVAILABLE
    assert lot.spots[0].type is SpotType.MANAGEMENT


def test_missing_lot_key_raises_clear_error():
    path = Path(__file__).parent / "fixtures" / "missing_key_lot.json"
    with pytest.raises(KeyMissingError, match="Lot is missing required key 'type'"):
        lot_loader.load(path)


def test_wrong_type_value_raises_error():
    path = Path(__file__).parent / "fixtures" / "wrong_key_type_lot.json"

    with pytest.raises(
        LotDescriptionKeyTypeError,
        match="Lot number must be an integer, got '32'",
    ):
        lot_loader.load(path)


def test_undefined_enum_raises_error():
    path = Path(__file__).parent / "fixtures" / "undefined_enum_lot.json"

    with pytest.raises(
        InvalidEnumError,
        match="Invalid lot status 'open'; expected OPEN, CLOSED, UNDER_MAINTENANCE",
    ):
        lot_loader.load(path)


def test_load_lot_rejects_duplicate_spot_numbers():
    path = Path(__file__).parent / "fixtures" / "duplicate_spot_number_lot.json"

    with pytest.raises(DuplicateSpotNumberError, match="Spot with given number already exists"):
        lot_loader.load(path)


def test_spot_without_floor_loads():
    path = Path(__file__).parent / "fixtures" / "valid_lot.json"
    lot = lot_loader.load(path)

    assert lot.spots[0].floor is None
