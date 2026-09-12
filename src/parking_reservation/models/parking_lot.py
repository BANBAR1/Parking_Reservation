from dataclasses import dataclass, field

from parking_reservation.models.enums import LotStatus, LotType, SpotStatus
from parking_reservation.models.location import Location
from parking_reservation.models.parking_spot import ParkingSpot


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
