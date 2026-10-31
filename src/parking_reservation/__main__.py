from datetime import datetime, timedelta
from pathlib import Path

from parking_reservation import booking_file, seed
from parking_reservation.errors import ReservationError
from parking_reservation.models import Driver, LotCollection, SpotType, Vehicle
from parking_reservation.reservation import BookingRequest, ReservationService


def main() -> None:
    data_path = Path(__file__).resolve().parents[2] / "data"
    lot_path = data_path / "parking_lot.json"
    booking_path = data_path / "booking.json"
    lots = LotCollection()
    for lot in seed.load(lot_path):
        lots.add(lot)

    service = ReservationService()
    if booking_path.exists():
        service.load_bookings(booking_file.load(booking_path, lots))
        print(f"Restored bookings: {service.bookings}")
        return

    lot = lots.get(32)
    spot = next(
        (candidate for candidate in lot.available_spots if candidate.type is SpotType.DISABLED),
        None,
    )
    if spot is None:
        raise RuntimeError(f"Parking lot {lot.number} has no available disabled spot for the demo")

    driver = Driver(name="Andrii")
    vehicle = Vehicle(license_plate="WZ12345", driver=driver)
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
    print(f"Cost: {booking.total}")

    try:
        service.reserve(booking_request)
    except ReservationError as error:
        print(f"Overlapping booking rejected: {error}")

    extra_lot = lots.get(74)
    extra_start_time = datetime(2127, 9, 20, 9, 0, tzinfo=extra_lot.location.timezone)
    for spot_number, license_plate in ((1, "WZ12346"), (2, "WZ12347")):
        extra_spot = next(
            (
                candidate
                for candidate in extra_lot.available_spots
                if candidate.number == spot_number
            ),
            None,
        )
        if extra_spot is None:
            raise RuntimeError(
                f"Parking lot {extra_lot.number} has no available spot {spot_number} for the demo"
            )

        extra_request = BookingRequest(
            lot=extra_lot,
            spot=extra_spot,
            vehicle=Vehicle(license_plate=license_plate, driver=driver),
            start_time=extra_start_time,
            end_time=extra_start_time + timedelta(hours=2),
        )
        extra_booking = service.reserve(extra_request)
        print(f"Created booking for lot {extra_lot.number}, spot {extra_booking.spot.number}")

    service.cancel(booking)
    print(f"Bookings after cancellation: {len(service.bookings)}")
    booking_file.save(service.bookings, booking_path)
    bookings = booking_file.load(booking_path, lots)
    service.load_bookings(bookings)
    print(f"Restored bookings: {service.bookings}")


if __name__ == "__main__":
    main()
