from datetime import datetime

from parking_reservation.models.booking import Booking
from parking_reservation.models.driver import Driver
from parking_reservation.models.enums import SpotStatus, SpotType
from parking_reservation.models.parking_spot import ParkingSpot
from parking_reservation.models.vehicle import Vehicle


def main() -> None:
    driver = Driver(name="Andrii")
    vehicle = Vehicle(license_plate="WZ12345", driver=driver)
    spot = ParkingSpot(number=12, status=SpotStatus.AVAILABLE, type=SpotType.DISABLED)

    booking = Booking(
        spot=spot,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 12, 30),
    )

    print(booking)
    print(f"Duration: {booking.duration_hours()} h")
    print(f"Cost: {booking.total_cost():.2f}")


if __name__ == "__main__":
    main()
