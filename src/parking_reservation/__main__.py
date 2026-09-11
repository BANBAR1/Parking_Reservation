from datetime import datetime

from parking_reservation.models.booking import Booking
from parking_reservation.models.driver import Driver
from parking_reservation.models.enums import (
    LocationType,
    LotStatus,
    LotType,
    SpotStatus,
    SpotType,
)
from parking_reservation.models.location import Location
from parking_reservation.models.parking_lot import ParkingLot
from parking_reservation.models.parking_spot import ParkingSpot
from parking_reservation.models.vehicle import Vehicle


def main() -> None:
    driver = Driver(name="Andrii")
    vehicle = Vehicle(license_plate="WZ12345", driver=driver)
    spot1 = ParkingSpot(number=12, status=SpotStatus.AVAILABLE, type=SpotType.DISABLED)
    spot2 = ParkingSpot(
        number=10,
        status=SpotStatus.OUT_OF_SERVICE,
        type=SpotType.ELECTRIC_VEHICLES,
    )
    spot3 = ParkingSpot(number=7, status=SpotStatus.RESERVED, type=SpotType.MANAGEMENT)
    spot4 = ParkingSpot(number=1, status=SpotStatus.OCCUPIED, type=SpotType.GENERAL)
    location = Location(type=LocationType.RESIDENTIAL, address="Washington")
    lot = ParkingLot(
        number=32,
        status=LotStatus.OPEN,
        type=LotType.PUBLIC,
        location=location,
        spots=[spot1, spot2, spot3, spot4],
    )

    booking = Booking(
        spot=spot1,
        vehicle=vehicle,
        start_time=datetime(2026, 9, 1, 9, 0),
        end_time=datetime(2026, 9, 1, 12, 30),
    )

    print(lot.spots[0].type)
    print(lot.spots[1].type)
    print(lot.spots[2].number)
    print(lot.spots[1].status)
    print(lot.location)
    print(lot.type)
    print(booking)
    print(f"Duration: {booking.duration_hours()} h")
    print(f"Cost: {booking.total_cost():.2f}")


if __name__ == "__main__":
    main()
