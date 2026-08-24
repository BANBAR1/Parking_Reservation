from dataclasses import dataclass
from Models.enums import LocationType


@dataclass
class Location:
    type: LocationType
    address: str
    name: str | None