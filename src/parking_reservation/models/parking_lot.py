from dataclasses import dataclass

from parking_reservation.models.enums import LotStatus, LotType


@dataclass
class ParkingLot:
    number: int
    floor: int | None
    status: LotStatus
    type: LotType
