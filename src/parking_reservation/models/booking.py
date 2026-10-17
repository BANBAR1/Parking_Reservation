from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from parking_reservation.models.parking import ParkingLot, ParkingSpot
from parking_reservation.pricing import PricingRule, rate_for, rule_for
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
    pricing_rule: PricingRule = field(init=False)
    hourly_rate: Decimal = field(init=False)
    total: Decimal = field(init=False)

    def __post_init__(self) -> None:
        self.hourly_rate = rate_for(self.spot.type)
        self.start_time = as_utc(self.start_time, "start_time")
        self.end_time = as_utc(self.end_time, "end_time")
        self.pricing_rule = rule_for(self.spot.type)
        self.total = self._cost_at_creation()

    def _cost_at_creation(self) -> Decimal:
        duration = self.end_time - self.start_time
        return self.pricing_rule.calculate(rate=self.hourly_rate, duration=duration)

    def duration_hours(self) -> Decimal:
        return Decimal((self.end_time - self.start_time).total_seconds() / 3600).quantize(
            Decimal("0.01"), "ROUND_HALF_UP"
        )

    def total_cost(self) -> Decimal:
        return self.total
