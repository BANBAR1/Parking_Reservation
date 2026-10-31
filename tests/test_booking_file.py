import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from parking_reservation import booking_file
from parking_reservation.errors import (
    InvalidTimezoneError,
    SpotAlreadyBookedError,
    SpotNotFoundError,
)
from parking_reservation.models import Booking, LotCollection, SpotType
from parking_reservation.models.booking import BookingStatus
from parking_reservation.pricing import DEFAULT_HOURLY_RATES, rate_for
from parking_reservation.reservation import BookingRequest, ReservationService


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
    service = ReservationService(clock=lambda: datetime(2027, 3, 1, 8, 0, tzinfo=UTC))
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    booking = service.reserve(_request(lot, spot, vehicle, start))
    path = tmp_path / "bookings.json"

    booking_file.save(service.bookings, path)
    loaded = booking_file.load(path, lots)

    assert loaded == [booking]
    assert loaded[0].lot is lot
    assert loaded[0].spot is spot


def test_save_writes_right_json_format(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    service = ReservationService(clock=lambda: datetime(2027, 3, 1, 8, 0, tzinfo=UTC))
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


def test_loaded_booking_blocks_overlapping_reservation(tmp_path, make_lot, spot, vehicle, location):
    lot = make_lot(spot)
    lots = LotCollection()
    lots.add(lot)
    start = datetime(2027, 3, 2, 9, 0, tzinfo=location.timezone)
    now = datetime(2027, 3, 1, 8, 0, tzinfo=UTC)
    original_service = ReservationService(clock=lambda: now)
    original_service.reserve(_request(lot, spot, vehicle, start))
    path = tmp_path / "bookings.json"
    booking_file.save(original_service.bookings, path)

    restored_service = ReservationService(clock=lambda: now)
    restored_service.load_bookings(booking_file.load(path, lots))

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
    original_service = ReservationService(clock=lambda: now)
    booking = original_service.reserve(_request(lot, spot, vehicle, start))
    original_service.cancel(booking)
    path = tmp_path / "bookings.json"
    booking_file.save(original_service.bookings, path)

    restored_service = ReservationService(clock=lambda: now)
    restored_service.load_bookings(booking_file.load(path, lots))

    assert restored_service.bookings[0].status is BookingStatus.CANCELLED
    restored_service.reserve(_request(lot, spot, vehicle, start))


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

    loaded = booking_file.load(path, lots)

    service = ReservationService()
    service.load_bookings(loaded)
    assert service.bookings == [booking]


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
