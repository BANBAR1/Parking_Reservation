from dataclasses import dataclass, field

from parking_reservation.errors import DuplicateLotNumberError, LotNotFoundError
from parking_reservation.models import ParkingLot


@dataclass
class LotCollection:
    _lots: dict[int, ParkingLot] = field(default_factory=dict[int, ParkingLot])

    def add(self, lot: ParkingLot) -> None:
        if lot.number in self._lots:
            raise DuplicateLotNumberError(
                f"Lot with number: {lot.number} already exists in this collection"
            )

        self._lots[lot.number] = lot

    def get(self, number: int) -> ParkingLot:
        try:
            return self._lots[number]
        except KeyError:
            raise LotNotFoundError(f"Lot with number {number} does not exist in this collection")
