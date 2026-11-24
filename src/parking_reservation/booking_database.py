from dataclasses import dataclass, field

import psycopg

from parking_reservation.models import Booking, BookingStatus, Driver, LotCollection, Vehicle


@dataclass
class BookingDatabase:
    database_url: str
    lots: LotCollection
    _connection: psycopg.Connection = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._connection = psycopg.connect(self.database_url, autocommit=True)

    def all(self) -> list[Booking]:
        rows = self._connection.execute("""
            SELECT
                id, lot, spot, license_plate, driver,
                start_time, end_time, hourly_rate, total, status
            FROM bookings
            """).fetchall()

        bookings: list[Booking] = []
        for row in rows:
            (
                booking_id,
                lot_number,
                spot_number,
                license_plate,
                driver_name,
                start_time,
                end_time,
                hourly_rate,
                total,
                status,
            ) = row

            lot = self.lots.get(lot_number)
            bookings.append(
                Booking(
                    id=booking_id,
                    lot=lot,
                    spot=lot.get_spot(spot_number),
                    vehicle=Vehicle(
                        license_plate=license_plate,
                        driver=Driver(name=driver_name),
                    ),
                    start_time=start_time,
                    end_time=end_time,
                    hourly_rate=hourly_rate,
                    total=total,
                    status=BookingStatus(status),
                )
            )

        return bookings

    def add(self, booking: Booking) -> None:
        self._connection.execute(
            """
            INSERT INTO bookings (
                id, lot, spot, license_plate, driver,
                start_time, end_time, hourly_rate, total, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                booking.id,
                booking.lot.number,
                booking.spot.number,
                booking.vehicle.license_plate,
                booking.vehicle.driver.name,
                booking.start_time,
                booking.end_time,
                booking.hourly_rate,
                booking.total,
                booking.status.value,
            ),
        )

    def update(self, booking: Booking) -> None:
        self._connection.execute(
            "UPDATE bookings SET status = %s WHERE id = %s",
            (booking.status.value, booking.id),
        )
