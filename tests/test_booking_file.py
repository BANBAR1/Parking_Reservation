import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from parking_reservation import booking_file
from parking_reservation.booking_file import BookingFile
from parking_reservation.errors import (
    BookingCancellationError,
    InvalidTimezoneError,
    SpotAlreadyBookedError,
    SpotNotFoundError,
)
from parking_reservation.models import Booking, BookingStatus, LotCollection, SpotType
from parking_reservation.pricing import DEFAULT_HOURLY_RATES, rate_for
from parking_reservation.reservation import (
    BookingMemory,
    BookingRequest,
    ReservationService,
)


def _request(lot, spot, vehicle, start):
    return BookingRequest(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=start,
        end_time=start + timedelta(hours=2),
    )


def test_load_returns_equal_bookings_referencing_existing_lot_and_spot(
    tmp_path, make_lot, spot, vehicle, location
):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    service = ReservationService(
        storage=BookingMemory(), clock=lambda: datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    )
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    booking = service.reserve(_request(lot, spot, vehicle, start))
    path = tmp_path / "bookings.json"

    booking_file.save(service.bookings, path)
    loaded = booking_file.load(path, lots)

    assert [vars(loaded_booking) for loaded_booking in loaded] == [vars(booking)]
    assert loaded[0].lot is lot
    assert loaded[0].spot is spot


def test_save_writes_right_json_format(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    service = ReservationService(
        storage=BookingMemory(), clock=lambda: datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    )
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    service.reserve(_request(lot, spot, vehicle, start))
    path = tmp_path / "bookings.json"

    booking_file.save(service.bookings, path)

    saved_data = json.loads(path.read_text(encoding="utf-8"))
    assert saved_data[0]["lot"] == lot.number
    assert saved_data[0]["spot"] == spot.number
    assert saved_data[0]["start_time"].endswith("+00:00")
    assert saved_data[0]["end_time"].endswith("+00:00")
    assert saved_data[0]["hourly_rate"] == "2.50"
    assert saved_data[0]["total"] == "5.00"


def test_reserve_saves_booking_to_file(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    path = tmp_path / "bookings.json"
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)

    booking = service.reserve(_request(lot, spot, vehicle, start))
    restored_service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)

    assert [vars(restored_booking) for restored_booking in restored_service.bookings] == [
        vars(booking)
    ]


def test_refused_reservation_does_not_change_file(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    path = tmp_path / "bookings.json"
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)
    service.reserve(_request(lot, spot, vehicle, start))
    contents_before = path.read_text(encoding="utf-8")

    with pytest.raises(SpotAlreadyBookedError):
        service.reserve(_request(lot, spot, vehicle, start))

    assert path.read_text(encoding="utf-8") == contents_before
    assert len(booking_file.load(path, lots)) == 1


def test_first_start_with_missing_file_has_no_bookings(tmp_path, make_lot, spot):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    path = tmp_path / "bookings.json"

    service = ReservationService(storage=BookingFile(path, lots))

    assert service.bookings == []


def test_bookings_from_file_storage_are_a_copy(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    path = tmp_path / "bookings.json"
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)
    booking = service.reserve(_request(lot, spot, vehicle, start))

    service.bookings.clear()

    assert service.bookings == [booking]


def test_loaded_booking_blocks_overlapping_reservation(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    path = tmp_path / "bookings.json"
    original_service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)
    original_service.reserve(_request(lot, spot, vehicle, start))

    restored_service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)

    with pytest.raises(SpotAlreadyBookedError):
        restored_service.reserve(_request(lot, spot, vehicle, start))


def test_load_restores_cancelled_status_and_allows_rebooking(
    tmp_path, make_lot, spot, vehicle, location
):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    path = tmp_path / "bookings.json"
    original_service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)
    booking = original_service.reserve(_request(lot, spot, vehicle, start))
    original_service.cancel(booking)

    restored_service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)

    assert restored_service.bookings[0].status is BookingStatus.CANCELLED
    restored_service.reserve(_request(lot, spot, vehicle, start))


def test_booking_from_before_a_restart_can_be_cancelled(
    tmp_path, make_lot, spot, vehicle, location
):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    path = tmp_path / "bookings.json"
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)
    booking = service.reserve(_request(lot, spot, vehicle, start))
    restarted = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)

    restarted.cancel(booking)

    assert booking_file.load(path, lots)[0].status is BookingStatus.CANCELLED


def test_booking_cancelled_after_a_restart_cannot_be_cancelled_again(
    tmp_path, make_lot, spot, vehicle, location
):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    path = tmp_path / "bookings.json"
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    service = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)
    booking = service.reserve(_request(lot, spot, vehicle, start))
    restarted = ReservationService(storage=BookingFile(path, lots), clock=lambda: now)
    restarted.cancel(booking)

    with pytest.raises(BookingCancellationError, match="Cannot cancel already cancelled booking"):
        restarted.cancel(booking)


def test_load_restores_past_booking_without_reserving(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    start = datetime(2020, 3, 2, 9, 0, tzinfo=location.timezone)
    booking = Booking(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=start,
        end_time=start + timedelta(hours=2),
        hourly_rate=Decimal("2.50"),
        total=Decimal("5.00"),
    )
    path = tmp_path / "bookings.json"
    booking_file.save([booking], path)

    service = ReservationService(storage=BookingFile(path, lots))
    assert [vars(service_booking) for service_booking in service.bookings] == [vars(booking)]


def test_load_preserves_saved_total_after_rate_change(
    tmp_path, make_lot, spot, vehicle, location, monkeypatch
):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    booking = Booking(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=start,
        end_time=start + timedelta(hours=2),
        hourly_rate=rate_for(spot.type),
        total=Decimal("5.00"),
    )
    path = tmp_path / "bookings.json"
    booking_file.save([booking], path)

    monkeypatch.setitem(DEFAULT_HOURLY_RATES, SpotType.GENERAL, Decimal("9.00"))
    loaded = booking_file.load(path, lots)

    assert loaded[0].hourly_rate == Decimal("2.50")
    assert loaded[0].total == Decimal("5.00")


def test_load_raises_when_spot_number_is_unknown(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    booking = Booking(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=start,
        end_time=start + timedelta(hours=2),
        hourly_rate=Decimal("2.50"),
        total=Decimal("5.00"),
    )
    path = tmp_path / "bookings.json"
    booking_file.save([booking], path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data[0]["spot"] = 999
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SpotNotFoundError):
        booking_file.load(path, lots)


def test_load_rejects_times_without_timezone_offset(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    booking = Booking(
        lot=lot,
        spot=spot,
        vehicle=vehicle,
        start_time=start,
        end_time=start + timedelta(hours=2),
        hourly_rate=Decimal("2.50"),
        total=Decimal("5.00"),
    )
    path = tmp_path / "bookings.json"
    booking_file.save([booking], path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data[0]["start_time"] = "2027-03-02T09:00:00"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(InvalidTimezoneError):
        booking_file.load(path, lots)
