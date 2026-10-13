from dataclasses import dataclass, field
from datetime import datetime

from parking_reservation.models.parking import ParkingLot, ParkingSpot
from parking_reservation.pricing import DEFAULT_HOURLY_RATES
from parking_reservation.timekeeping import as_utc


@dataclass
class Driver:
    name: str


@dataclass
class Vehicle:
    license_plate: str
    driver: Driver


@dataclass
class Booking:
    lot: ParkingLot
    spot: ParkingSpot
    vehicle: Vehicle
    start_time: datetime
    end_time: datetime
    hourly_rate: float = field(init=False)

    def __post_init__(self) -> None:
        self.hourly_rate = DEFAULT_HOURLY_RATES[self.spot.type]
        self.start_time = as_utc(self.start_time, "start_time")
        self.end_time = as_utc(self.end_time, "end_time")

    def duration_hours(self) -> float:
        return (self.end_time - self.start_time).total_seconds() / 3600

    def total_cost(self) -> float:
        return self.duration_hours() * self.hourly_rate
