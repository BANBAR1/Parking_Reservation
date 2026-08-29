from dataclasses import dataclass

from models.driver import Driver


@dataclass
class Vehicle:
    license_plate: str
    driver: Driver
