from dataclasses import dataclass, field
from datetime import datetime

from models.enums import DEFAULT_HOURLY_RATES
from models.parking_spot import ParkingSpot
from models.vehicle import Vehicle


@dataclass
class Booking:
    spot: ParkingSpot
    vehicle: Vehicle
    start_time: datetime
    end_time: datetime
    hourly_rate: float = field(init=False)

    def __post_init__(self) -> None:
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        self.hourly_rate = DEFAULT_HOURLY_RATES[self.spot.type]

    def duration_hours(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 3600

    def total_cost(self) -> float:
        return self.duration_hours() * self.hourly_rate
