from datetime import datetime
from pathlib import Path

from parking_reservation.errors import ReservationError
from parking_reservation.models import Driver, Vehicle
from parking_reservation.models.lot_collection import LotCollection
from parking_reservation.reservation import BookingRequest, ReservationService
from parking_reservation.utilities import lot_loader


def main() -> None:
    lot_path = Path(__file__).resolve().parents[2] / "data" / "parking_lot.json"
    lots = LotCollection()
    for lot in lot_loader.load(lot_path):
        lots.add(lot)
    lot = lots.get(32)
    available_spots = lot.available_spots
    if not available_spots:
        raise RuntimeError(f"Parking lot {lot.number} has no available spots for the demo")
    spot = available_spots[0]

    driver = Driver(name="Andrii")
    vehicle = Vehicle(license_plate="WZ12345", driver=driver)

    service = ReservationService()
    start_time = datetime(2127, 9, 20, 9, 0)
    end_time = datetime(2127, 9, 20, 12, 30)
    booking_request = BookingRequest(
        lot=lot,
        spot=spot,
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
                spot=spot,
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
