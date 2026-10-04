import json
from pathlib import Path
from typing import TypeGuard

from parking_reservation.errors import (
    InvalidLocationTypeError,
    InvalidLotStatusError,
    InvalidLotTypeError,
    InvalidSpotStatusError,
    InvalidSpotTypeError,
    KeyMissingError,
    LotDescriptionError,
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


def _is_string_keyed_dict(value: object) -> TypeGuard[dict[str, object]]:

    return isinstance(value, dict)


def _is_object_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


class LotLoader:
    def __init__(self, path: Path):
        self.path = path

    def load_lot(self) -> ParkingLot:
        with self.path.open() as file:
            data: object = json.load(file)

        return LotLoader.lot_from_dict(data)

    @staticmethod
    def lot_from_dict(data: object) -> ParkingLot:
        if not _is_string_keyed_dict(data):
            raise LotDescriptionError
        for key in ("number", "status", "type", "location", "spots"):
            if key not in data:
                raise KeyMissingError(f"Lot description is missing required key {key!r}")

        number = data["number"]
        if type(number) is not int:
            raise LotDescriptionKeyTypeError(f"Lot number {number!r} is not an integer")

        status_value = data["status"]
        if not isinstance(status_value, str):
            raise LotDescriptionKeyTypeError(f"Lot status value {status_value!r} is not a string")
        try:
            status = LotStatus(status_value)
        except ValueError:
            raise InvalidLotStatusError(
                f"Invalid lot status {status_value!r}; expected OPEN, CLOSED, or UNDER_MAINTENANCE"
            )

        type_value = data["type"]
        if not isinstance(type_value, str):
            raise LotDescriptionKeyTypeError(f"Lot type value {type_value!r} is not a string")

        try:
            lot_type = LotType(type_value)
        except ValueError:
            raise InvalidLotTypeError(
                f"Invalid lot type {type_value!r}; expected PUBLIC or PRIVATE"
            )
        location = LotLoader.location_from_dict(data["location"])

        spots_value = data["spots"]
        if not _is_object_list(spots_value):
            raise LotDescriptionKeyTypeError("'spots' must be a list")

        spots: list[ParkingSpot] = []
        for spot in spots_value:
            spots.append(LotLoader.spot_from_dict(spot))

        return ParkingLot(number, status, lot_type, location, spots)

    @staticmethod
    def spot_from_dict(data: object) -> ParkingSpot:
        if not _is_string_keyed_dict(data):
            raise LotDescriptionKeyTypeError("Spot data must be an object with string keys")

        for key in ("number", "status", "type"):
            if key not in data:
                raise KeyMissingError(f"Spot description is missing required key {key!r}")

        if type(data["number"]) is not int:
            raise LotDescriptionKeyTypeError(f"Spot number {data['number']!r} is not an integer")

        number = data["number"]

        if not isinstance(data["status"], str):
            raise LotDescriptionKeyTypeError(f"Spot status {data['status']!r} is not a string")

        try:
            status = SpotStatus(data["status"])
        except ValueError:
            raise InvalidSpotStatusError(
                f"Invalid spot status {data['status']!r} for spot {number}; "
                "expected AVAILABLE or OUT_OF_SERVICE"
            )

        if not isinstance(data["type"], str):
            raise LotDescriptionKeyTypeError(
                f"Spot type {data['type']!r} for spot {number} is not a string"
            )
        try:
            spot_type = SpotType(data["type"])
        except ValueError:
            raise InvalidSpotTypeError(
                f"Invalid spot type {data['type']!r} for spot {number}; "
                "expected DISABLED, WORKERS, VISITORS, ELECTRIC_VEHICLES, MANAGEMENT, or GENERAL"
            )
        floor = data.get("floor")
        if floor is not None and type(floor) is not int:
            raise LotDescriptionKeyTypeError(
                f"Spot floor {floor!r} for spot {number} must be an integer or null"
            )
        return ParkingSpot(
            number,
            status,
            spot_type,
            floor,
        )

    @staticmethod
    def location_from_dict(data: object) -> Location:
        if not _is_string_keyed_dict(data):
            raise LotDescriptionKeyTypeError("Location data must be an object with string keys")

        for key in ("type", "address"):
            if key not in data:
                raise KeyMissingError(f"Location description is missing required key {key!r}")

        if not isinstance(data["type"], str):
            raise LotDescriptionKeyTypeError(f"Location type {data['type']!r} is not a string")

        try:
            type = LocationType(data["type"])
        except ValueError:
            raise InvalidLocationTypeError(
                f"Invalid location type {data['type']!r} expected MALL, OFFICE, "
                "AIRPORT, HOSPITAL or RESIDENTIAL"
            )

        if not isinstance(data["address"], str):
            raise LotDescriptionKeyTypeError(
                f"Location address {data['address']!r} is not a string"
            )

        address = data["address"]

        return Location(type, address)
