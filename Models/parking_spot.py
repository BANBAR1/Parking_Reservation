from dataclasses import dataclass

from Models.enums import SpotStatus, SpotType


@dataclass
class ParkingSpot:
    number: int
    status: SpotStatus
    type: SpotType
