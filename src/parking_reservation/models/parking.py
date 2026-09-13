from dataclasses import dataclass, field
from enum import Enum


class SpotType(Enum):
    DISABLED = "DISABLED"
    WORKERS = "WORKERS"
    VISITORS = "VISITORS"
    ELECTRIC_VEHICLES = "ELECTRIC_VEHICLES"
    MANAGEMENT = "MANAGEMENT"
    GENERAL = "GENERAL"


class SpotStatus(Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


@dataclass
class ParkingSpot:
    number: int
    status: SpotStatus
    type: SpotType
    floor: int | None = None


class LotStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"


class LotType(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class LocationType(Enum):
    MALL = "MALL"
    OFFICE = "OFFICE"
    AIRPORT = "AIRPORT"
    HOSPITAL = "HOSPITAL"
    RESIDENTIAL = "RESIDENTIAL"


@dataclass
class Location:
    type: LocationType
    address: str
    name: str | None = None


@dataclass
class ParkingLot:
    number: int
    status: LotStatus
    type: LotType
    location: Location
    spots: list[ParkingSpot] = field(default_factory=list)

    @property
    def available_spots(self) -> list[ParkingSpot]:
        return [spot for spot in self.spots if spot.status is SpotStatus.AVAILABLE]

    @property
    def is_full(self) -> bool:
        return bool(self.spots) and not self.available_spots
