import json
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from parking_reservation.models import Booking, BookingStatus, Driver, LotCollection, Vehicle


def save(bookings: list[Booking], path: Path) -> None:
    data = [
        {
            "lot": booking.lot.number,
            "spot": booking.spot.number,
            "vehicle": {
                "license_plate": booking.vehicle.license_plate,
                "driver": booking.vehicle.driver.name,
            },
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "hourly_rate": str(booking.hourly_rate),
            "total": str(booking.total),
            "status": booking.status.value,
            "id": str(booking.id),
        }
        for booking in bookings
    ]

    with path.open(mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
        file.write("\n")


def load(path: Path, lots: LotCollection) -> list[Booking]:
    bookings: list[Booking] = []
    with path.open(encoding="utf-8") as file:
        data: list[dict[str, Any]] = json.load(file)
        for booking in data:
            lot = lots.get(booking["lot"])
            bookings.append(
                Booking(
                    lot=lot,
                    spot=lot.get_spot(booking["spot"]),
                    vehicle=Vehicle(
                        license_plate=booking["vehicle"]["license_plate"],
                        driver=Driver(name=booking["vehicle"]["driver"]),
                    ),
                    start_time=datetime.fromisoformat(booking["start_time"]),
                    end_time=datetime.fromisoformat(booking["end_time"]),
                    hourly_rate=Decimal(booking["hourly_rate"]),
                    total=Decimal(booking["total"]),
                    status=BookingStatus(booking["status"]),
                    id=UUID(booking["id"]),
                )
            )
    return bookings


@dataclass
class BookingFile:
    path: Path
    lots: LotCollection
    _bookings: list[Booking] = field(default_factory=list[Booking], init=False)

    def __post_init__(self) -> None:
        try:
            self._bookings: list[Booking] = load(self.path, self.lots)
        except FileNotFoundError:
            self._bookings = []

    def all(self) -> list[Booking]:
        return self._bookings.copy()

    def add(self, booking: Booking) -> None:
        self._bookings.append(booking)
        save(self._bookings, self.path)

    def update(self, booking: Booking) -> None:
        save(self._bookings, self.path)
