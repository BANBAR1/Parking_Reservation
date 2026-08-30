from dataclasses import dataclass

from parking_reservation.models.driver import Driver


@dataclass
class Vehicle:
    license_plate: str
    driver: Driver
