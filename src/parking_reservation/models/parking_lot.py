from dataclasses import dataclass, field

from parking_reservation.models.enums import LotStatus, LotType
from parking_reservation.models.location import Location
from parking_reservation.models.parking_spot import ParkingSpot


@dataclass
class ParkingLot:
    number: int
    status: LotStatus
    type: LotType
    location: Location
    spots: list[ParkingSpot] = field(default_factory=list)
