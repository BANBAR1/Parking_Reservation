from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import Protocol

from parking_reservation.models.parking import SpotType

DEFAULT_HOURLY_RATES: dict[SpotType, Decimal] = {
    SpotType.GENERAL: Decimal("2.50"),
    SpotType.DISABLED: Decimal("1.00"),
    SpotType.ELECTRIC_VEHICLES: Decimal("3.50"),
    SpotType.MANAGEMENT: Decimal("0.0"),
    SpotType.WORKERS: Decimal("0.0"),
    SpotType.VISITORS: Decimal("0.0"),
}


def rate_for(spot_type: SpotType) -> Decimal:
    return DEFAULT_HOURLY_RATES[spot_type]


def get_microseconds(duration: timedelta) -> int:
    return duration // timedelta(microseconds=1)


def get_hours(duration: timedelta) -> Decimal:
    return Decimal(get_microseconds(duration)) / Decimal("3600000000")


class PricingRule(Protocol):
    def calculate(self, rate: Decimal, duration: timedelta) -> Decimal: ...


@dataclass(frozen=True)
class HourlyPricingRule:
    def calculate(self, rate: Decimal, duration: timedelta) -> Decimal:
        duration_hours = get_hours(duration)
        return (rate * duration_hours).quantize(Decimal("0.01"), "ROUND_UP")


@dataclass(frozen=True)
class DailyCapPricing:
    daily_cap: Decimal = Decimal("15.00")

    def calculate(self, rate: Decimal, duration: timedelta) -> Decimal:
        remaining = duration
        price = Decimal("0.00")
        period = timedelta(hours=24)

        while remaining > timedelta(0):
            chunk = min(remaining, period)
            hourly_charge = HourlyPricingRule().calculate(rate=rate, duration=chunk)
            price += min(hourly_charge, self.daily_cap)
            remaining -= chunk

        return price


@dataclass(frozen=True)
class FreePricingRule:
    def calculate(self, rate: Decimal, duration: timedelta) -> Decimal:
        return Decimal("0.00")


DEFAULT_PRICING_RULE_FACTORIES: dict[SpotType, Callable[[], PricingRule]] = {
    SpotType.GENERAL: DailyCapPricing,
    SpotType.DISABLED: DailyCapPricing,
    SpotType.ELECTRIC_VEHICLES: DailyCapPricing,
    SpotType.MANAGEMENT: FreePricingRule,
    SpotType.WORKERS: FreePricingRule,
    SpotType.VISITORS: FreePricingRule,
}


def rule_for(spot_type: SpotType) -> PricingRule:
    return DEFAULT_PRICING_RULE_FACTORIES[spot_type]()
