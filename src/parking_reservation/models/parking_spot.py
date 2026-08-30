from dataclasses import dataclass

from parking_reservation.models.enums import SpotStatus, SpotType


@dataclass
class ParkingSpot:
    number: int
    status: SpotStatus
    type: SpotType
