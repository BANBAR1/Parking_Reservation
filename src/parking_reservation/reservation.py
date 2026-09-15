from dataclasses import dataclass, field
from datetime import datetime

from parking_reservation.models import Booking, ParkingLot, SpotStatus, Vehicle


@dataclass
class ReservationService:
    bookings: list[Booking] = field(default_factory=list)

    def reserve(
        self, lot: ParkingLot, vehicle: Vehicle, start_time: datetime, end_time: datetime
    ) -> Booking:
        if not lot.available_spots:
            raise ValueError(f"No available spots in lot number: {lot.number}")

        spot = lot.available_spots[0]
        booking = Booking(spot=spot, vehicle=vehicle, start_time=start_time, end_time=end_time)

        spot.status = SpotStatus.RESERVED

        self.bookings.append(booking)

        return booking

    def cancel(self, booking: Booking) -> None:

        for index, held_booking in enumerate(self.bookings):
            if held_booking is booking:
                booking.spot.status = SpotStatus.AVAILABLE
                self.bookings.pop(index)
                return

        raise ValueError(f"Booking number: {booking.spot.number} is not available")
