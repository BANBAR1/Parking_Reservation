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
    path = Path(__file__).parent / "fixtures" / "valid_lots.json"
    lot_list = lot_loader.load(path)
    lot = lot_list[0]

    assert lot.number == 32
    assert lot.location == Location(type=LocationType.RESIDENTIAL, address="Washington")
    assert len(lot.spots) == 3
    assert lot.spots[0].number == 3
    assert lot.spots[1].number == 5
    assert lot.spots[2].number == 6


def test_load_converts_enum_fields():
    path = Path(__file__).parent / "fixtures" / "valid_lots.json"
    lot_list = lot_loader.load(path)
    lot = lot_list[0]
    assert lot.status is LotStatus.OPEN
    assert lot.type is LotType.PUBLIC
    assert lot.location.type is LocationType.RESIDENTIAL
    assert lot.spots[0].status is SpotStatus.AVAILABLE
    assert lot.spots[0].type is SpotType.MANAGEMENT


def test_missing_lot_key_raises_clear_error():
    path = Path(__file__).parent / "fixtures" / "missing_key_lot.json"
    with pytest.raises(KeyMissingError, match="Lot is missing required key 'type'"):
        lot_loader.load(path)


def test_require_key_func_works():
    lot_loader._require_keys({"1": 1, "2": 2, "3": 3}, ("1", "2", "3"), "numbers")


def test_require_key_func_raises_error():
    with pytest.raises(
        KeyMissingError,
        match="numbers is missing required key '2'",
    ):
        lot_loader._require_keys({"1": 1, "3": 3}, ("1", "2", "3"), "numbers")


def test_as_enum_func_works():
    assert lot_loader._as_enum("PUBLIC", LotType, "Lot type") is LotType.PUBLIC


def test_as_enum_func_raises_error():

    with pytest.raises(
        InvalidEnumError,
        match=r"Invalid lot type 'Enum\?'; expected PUBLIC, PRIVATE",
    ):
        lot_loader._as_enum("Enum?", LotType, "lot type")


def test_as_str_func_works():
    text = lot_loader._as_str("Washington", "Lot address")
    assert text == "Washington"


def test_as_str_func_raises_error():
    with pytest.raises(
        LotDescriptionKeyTypeError,
        match="Lot address must be str, got 32",
    ):
        lot_loader._as_str(32, "Lot address")


def test_as_int_func_works():
    number = lot_loader._as_int(32, "Lot number")
    assert number == 32


def test_as_int_func_raises_error():
    with pytest.raises(
        LotDescriptionKeyTypeError,
        match="Lot number must be an integer, got True",
    ):
        lot_loader._as_int(True, "Lot number")


def test_as_list_func_works():
    items = [1, 2, 3]
    assert lot_loader._as_list(items, "Lot spots") is items


def test_as_list_func_raises_error():
    with pytest.raises(
        LotDescriptionKeyTypeError,
        match="Lot spots must be list, got 'not a list'",
    ):
        lot_loader._as_list("not a list", "Lot spots")


def test_as_dict_func_works():
    data = {"number": 32}
    assert lot_loader._as_dict(data, "Lot description") is data


def test_as_dict_func_raises_error():
    with pytest.raises(
        LotDescriptionKeyTypeError,
        match="Lot description must be dict, got \\[\\]",
    ):
        lot_loader._as_dict([], "Lot description")


def test_load_rejects_duplicate_spot_numbers():
    path = Path(__file__).parent / "fixtures" / "duplicate_spot_number_lot.json"

    with pytest.raises(DuplicateSpotNumberError, match="Spot with given number already exists"):
        lot_loader.load(path)


def test_spot_without_floor_loads():
    path = Path(__file__).parent / "fixtures" / "valid_lots.json"
    lot_list = lot_loader.load(path)
    lot = lot_list[0]

    assert lot.spots[0].floor is None


def test_spot_with_floor_loads():
    path = Path(__file__).parent / "fixtures" / "valid_lots.json"
    lot_list = lot_loader.load(path)
    lot = lot_list[0]

    assert lot.spots[2].floor == 2
