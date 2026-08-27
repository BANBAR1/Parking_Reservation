from dataclasses import dataclass

from models.enums import LocationType


@dataclass
class Location:
    type: LocationType
    address: str
    name: str | None
