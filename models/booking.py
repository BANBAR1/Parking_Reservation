from dataclasses import dataclass
from datetime import datetime

from models.driver import Driver
from models.parking_spot import ParkingSpot


@dataclass
class Booking:
    spot: ParkingSpot
    driver: Driver
    start_time: datetime
    end_time: datetime

    def __post_init__(self) -> None:
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")

    def duration_hours(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 3600

    def total_cost(self) -> float:
        return self.duration_hours() * self.spot.hourly_rate
