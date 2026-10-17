from datetime import datetime
from pathlib import Path

from parking_reservation.errors import ReservationError
from parking_reservation.models import Driver, LotCollection, SpotType, Vehicle
from parking_reservation.reservation import BookingRequest, ReservationService
from parking_reservation.utilities import lot_loader


def main() -> None:
    lot_path = Path(__file__).resolve().parents[2] / "data" / "parking_lot.json"
    lots = LotCollection()
    for lot in lot_loader.load(lot_path):
        lots.add(lot)
    lot = lots.get(32)
    spot = next(
        (candidate for candidate in lot.available_spots if candidate.type is SpotType.DISABLED),
        None,
    )
    if spot is None:
        raise RuntimeError(f"Parking lot {lot.number} has no available disabled spot for the demo")

    driver = Driver(name="Andrii")
    vehicle = Vehicle(license_plate="WZ12345", driver=driver)
    service = ReservationService()
    start_time = datetime(2127, 9, 20, 0, 0, tzinfo=lot.location.timezone)
    end_time = datetime(2127, 9, 20, 0, 20, tzinfo=lot.location.timezone)
    booking_request = BookingRequest(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=start_time,
        end_time=end_time,
    )

    booking = service.reserve(booking_request)

    print(f"Created booking for spot {booking.spot.number}")
    print(f"Duration: {booking.duration_hours():.2f} h")
    print(f"Cost: {booking.total_cost()}")

    try:
        service.reserve(booking_request)
    except ReservationError as error:
        print(f"Overlapping booking rejected: {error}")

    service.cancel(booking)
    print(f"Bookings after cancellation: {len(service.bookings)}")


if __name__ == "__main__":
    main()
