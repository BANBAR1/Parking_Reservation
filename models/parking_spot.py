from dataclasses import dataclass

from models.enums import SpotStatus, SpotType


@dataclass
class ParkingSpot:
    number: int
    status: SpotStatus
    type: SpotType
