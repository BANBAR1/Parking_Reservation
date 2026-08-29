from datetime import datetime

from models.booking import Booking
from models.driver import Driver
from models.enums import SpotStatus, SpotType
from models.parking_spot import ParkingSpot


def main() -> None:
    driver = Driver(name="Andrii", license_plate="WZ12345")
    spot = ParkingSpot(
        number=12,
        status=SpotStatus.AVAILABLE,
        type=SpotType.GENERAL,
        hourly_rate=3.0,
    )

    booking = Booking(
        spot=spot,
        driver=driver,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 12, 30),
    )

    print(booking)
    print(f"Duration: {booking.duration_hours()} h")
    print(f"Cost: {booking.total_cost():.2f}")


if __name__ == "__main__":
    main()
