from dataclasses import dataclass

from models.enums import SpotStatus, SpotType


@dataclass
class ParkingSpot:
    number: int
    status: SpotStatus
    type: SpotType
    hourly_rate: float = 2.50
