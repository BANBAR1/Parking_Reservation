from dataclasses import dataclass, field
from datetime import datetime

from models.vehicle import Vehicle
from models.parking_spot import ParkingSpot


@dataclass
class Booking:
    spot: ParkingSpot
    vehicle: Vehicle
    start_time: datetime
    end_time: datetime
    rate_at_booking: float = field(init=False)


    def __post_init__(self) -> None:
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        self.rate_at_booking = self.spot.hourly_rate

    def duration_hours(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 3600

    def total_cost(self) -> float:
        return self.duration_hours() * self.rate_at_booking
