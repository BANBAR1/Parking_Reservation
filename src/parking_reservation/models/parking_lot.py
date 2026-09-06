from dataclasses import dataclass

from parking_reservation.models.enums import LotStatus, LotType


@dataclass
class ParkingLot:
    number: int
    status: LotStatus
    type: LotType
    floor: int | None = None
