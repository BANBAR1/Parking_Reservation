from parking_reservation.models.enums import SpotType

DEFAULT_HOURLY_RATES: dict[SpotType, float] = {
    SpotType.GENERAL: 2.50,
    SpotType.DISABLED: 1.00,
    SpotType.ELECTRIC_VEHICLES: 3.50,
    SpotType.MANAGEMENT: 0.0,
    SpotType.WORKERS: 0.0,
    SpotType.VISITORS: 0.0,
}
