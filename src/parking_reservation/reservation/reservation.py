from dataclasses import dataclass, field
from datetime import datetime

from parking_reservation.models import Booking, ParkingLot, ParkingSpot, Vehicle


@dataclass
class BookingRequest:
    lot: ParkingLot
    spot: ParkingSpot
    vehicle: Vehicle
    start_time: datetime
    end_time: datetime


# Todo: Optimize performance
@dataclass
class ReservationService:
    bookings: list[Booking] = field(default_factory=list)

    def reserve(self, request: BookingRequest) -> Booking:
        lot = request.lot
        spot = request.spot
        vehicle = request.vehicle
        start_time = request.start_time
        end_time = request.end_time

        if self.__is_request_valid(request):
            booking = Booking(
                lot=lot, spot=spot, vehicle=vehicle, start_time=start_time, end_time=end_time
            )

            self.bookings.append(booking)

            return booking
        raise ValueError("Request is not valid")

    def cancel(self, booking: Booking) -> None:

        for index, held_booking in enumerate(self.bookings):
            if held_booking is booking:
                self.bookings.pop(index)
                return

        raise ValueError("Booking was not found")

    def __is_request_valid(self, request: BookingRequest) -> bool:
        lot = request.lot
        spot = request.spot
        start_time = request.start_time
        end_time = request.end_time
        date_now = datetime.now()
        matched_bookings = [booking for booking in self.__active_bookings() if spot is booking.spot]

        if not lot.available_spots:
            return False

        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")

        if start_time < date_now:
            return False

        for booking in matched_bookings:
            if start_time < booking.end_time and end_time > booking.start_time:
                return False

        return True

    def __active_bookings(self) -> list[Booking]:

        return [booking for booking in self.bookings if booking.end_time > datetime.now()]
