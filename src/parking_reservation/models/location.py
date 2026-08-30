from dataclasses import dataclass

from parking_reservation.models.enums import LocationType


@dataclass
class Location:
    type: LocationType
    address: str
    name: str | None
