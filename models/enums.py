from enum import Enum


class SpotType(Enum):
    DISABLED = "FOR_DISABLED"
    WORKERS = "FOR_WORKERS"
    VISITORS = "FOR_VISITORS"
    ELECTRIC_VEHICLES = "FOR_ELECTRIC_VEHICLES"
    MANAGEMENT = "FOR_MANAGEMENT"
    GENERAL = "GENERAL"


DEFAULT_HOURLY_RATES: dict[SpotType, float] = {
    SpotType.GENERAL: 2.50,
    SpotType.DISABLED: 1.00,
    SpotType.ELECTRIC_VEHICLES: 3.50,
    SpotType.MANAGEMENT: 0.0,
    SpotType.WORKERS: 0.0,
    SpotType.VISITORS: 0.0,
}


class SpotStatus(Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


class LotStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    FULL = "FULL"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"


class LotType(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class LocationType(Enum):
    MALL = "MALL"
    OFFICE = "OFFICE"
    AIRPORT = "AIRPORT"
    HOSPITAL = "HOSPITAL"
    RESIDENTIAL = "RESIDENTIAL"
