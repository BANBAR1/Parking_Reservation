from dataclasses import dataclass, field
from enum import Enum

from parking_reservation.errors import DuplicateSpotNumberError


class SpotType(Enum):
    DISABLED = "DISABLED"
    WORKERS = "WORKERS"
    VISITORS = "VISITORS"
    ELECTRIC_VEHICLES = "ELECTRIC_VEHICLES"
    MANAGEMENT = "MANAGEMENT"
    GENERAL = "GENERAL"


class SpotStatus(Enum):
    AVAILABLE = "AVAILABLE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


@dataclass
class ParkingSpot:
    number: int
    status: SpotStatus
    type: SpotType
    floor: int | None = None


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


class LotStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"


class LotType(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


@dataclass(init=False)
class ParkingLot:
    number: int
    status: LotStatus
    type: LotType
    location: Location
    _spots: list[ParkingSpot] = field(default_factory=list)

    def __init__(
        self,
        number: int,
        status: LotStatus,
        type: LotType,
        location: Location,
        spots: list[ParkingSpot] | None = None,
    ) -> None:
        self.number = number
        self.status = status
        self.type = type
        self.location = location
        self._spots = []
        if spots is not None:
            for spot in spots:
                self.add_spot(spot)

    @property
    def spots(self) -> list[ParkingSpot]:
        return self._spots.copy()

    @property
    def available_spots(self) -> list[ParkingSpot]:
        return [spot for spot in self._spots if spot.status is SpotStatus.AVAILABLE]

    @property
    def is_full(self) -> bool:
        return bool(self._spots) and not self.available_spots

    def add_spot(self, spot: ParkingSpot) -> None:
        if any(lot_spot.number == spot.number for lot_spot in self._spots):
            raise DuplicateSpotNumberError

        self._spots.append(spot)
