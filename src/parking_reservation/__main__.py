from datetime import datetime

from parking_reservation.errors import ReservationError
from parking_reservation.models import (
    Driver,
    Location,
    LocationType,
    LotStatus,
    LotType,
    ParkingLot,
    ParkingSpot,
    SpotStatus,
    SpotType,
    Vehicle,
)
from parking_reservation.reservation import BookingRequest, ReservationService


def main() -> None:
    driver = Driver(name="Andrii")
    vehicle = Vehicle(license_plate="WZ12345", driver=driver)
    spot1 = ParkingSpot(number=12, status=SpotStatus.AVAILABLE, type=SpotType.DISABLED)
    spot2 = ParkingSpot(
        number=10,
        status=SpotStatus.OUT_OF_SERVICE,
        type=SpotType.ELECTRIC_VEHICLES,
    )
    spot3 = ParkingSpot(number=7, status=SpotStatus.AVAILABLE, type=SpotType.MANAGEMENT)
    location = Location(type=LocationType.RESIDENTIAL, address="Washington")
    lot = ParkingLot(
        number=32,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1, spot2, spot3],
    )

    service = ReservationService()
    start_time = datetime(2127, 9, 20, 9, 0)
    end_time = datetime(2127, 9, 20, 12, 30)
    booking_request = BookingRequest(
        lot=lot,
        spot=spot1,
        vehicle=vehicle,
        start_time=start_time,
        end_time=end_time,
    )

    booking = service.reserve(booking_request)

    print(f"Created booking for spot {booking.spot.number}")
    print(f"Duration: {booking.duration_hours():.1f} h")
    print(f"Cost: {booking.total_cost():.2f}")

    try:
        service.reserve(
            BookingRequest(
                lot=lot,
                spot=spot1,
                vehicle=vehicle,
                start_time=datetime(2127, 9, 20, 11, 0),
                end_time=datetime(2127, 9, 20, 13, 0),
            )
        )
    except ReservationError as error:
        print(f"Overlapping booking rejected: {error}")

    service.cancel(booking)
    print(f"Bookings after cancellation: {len(service.bookings)}")


if __name__ == "__main__":
    main()
