import json
from enum import Enum
from pathlib import Path
from typing import TypeGuard

from parking_reservation.errors import (
    InvalidEnumError,
    KeyMissingError,
    LotDescriptionKeyTypeError,
)
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


def load(path: Path) -> list[ParkingLot]:
    with path.open() as file:
        data: list[dict[str, object]] = json.load(file)
    return [from_dict(lot) for lot in data]


def from_dict(data: object) -> ParkingLot:
    lot = _as_dict(data, "Lot")
    _require_keys(lot, ("number", "status", "type", "location", "spots"), "Lot")
    return ParkingLot(
        number=_as_int(lot["number"], "Lot number"),
        status=_as_enum(lot["status"], LotStatus, "lot status"),
        type=_as_enum(lot["type"], LotType, "lot type"),
        location=_location_from_dict(lot["location"]),
        spots=[_spot_from_dict(item) for item in _as_list(lot["spots"], "Lot 'spots'")],
    )


def _spot_from_dict(data: object) -> ParkingSpot:
    spot = _as_dict(data, "Spot description")
    _require_keys(spot, ("number", "status", "type"), "Spot description")

    number = _as_int(spot["number"], "Spot number")

    floor = spot.get("floor")

    return ParkingSpot(
        number=number,
        status=_as_enum(spot["status"], SpotStatus, f"status for spot {number}"),
        type=_as_enum(spot["type"], SpotType, f"type for spot {number}"),
        floor=None if floor is None else _as_int(floor, f"floor for spot {number}"),
    )


def _location_from_dict(data: object) -> Location:
    location = _as_dict(data, "Location description")
    _require_keys(location, ("type", "address"), "Location description")

    return Location(
        type=_as_enum(location["type"], LocationType, "location type"),
        address=_as_str(location["address"], "location address"),
    )


def _as_enum[EnumT: Enum](value: object, enum_type: type[EnumT], what: str) -> EnumT:
    text = _as_str(value, what)
    try:
        return enum_type(text)
    except ValueError:
        expected = ", ".join(str(member.value) for member in enum_type)
        raise InvalidEnumError(f"Invalid {what} {text!r}; expected {expected}") from None


def _as_dict(value: object, what: str) -> dict[str, object]:
    if not _is_dict(value):
        raise LotDescriptionKeyTypeError(f"{what} must be dict, got {value!r}")
    return value


def _is_dict(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)


def _as_list(value: object, what: str) -> list[object]:
    if not _is_list(value):
        raise LotDescriptionKeyTypeError(f"{what} must be list, got {value!r}")
    return value


def _is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def _as_int(value: object, what: str) -> int:
    if type(value) is not int:
        raise LotDescriptionKeyTypeError(f"{what} must be an integer, got {value!r}")
    return value


def _as_str(value: object, what: str):
    if not isinstance(value, str):
        raise LotDescriptionKeyTypeError(f"{what} must be str, got {value!r}")
    return value


def _require_keys(data: dict[str, object], keys: tuple[str, ...], what: str) -> None:
    for key in keys:
        if key not in data:
            raise KeyMissingError(f"{what} is missing required key {key!r}")
