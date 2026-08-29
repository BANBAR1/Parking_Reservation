from dataclasses import dataclass

from models.enums import DEFAULT_HOURLY_RATES, SpotStatus, SpotType


@dataclass
class ParkingSpot:
    number: int
    status: SpotStatus
    type: SpotType
    hourly_rate: float | None = None

    def __post_init__(self):
        if self.hourly_rate is None:
            self.hourly_rate = DEFAULT_HOURLY_RATES[self.type]
