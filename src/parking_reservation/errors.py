class ParkingReservationError(Exception):
    message = "Something went wrong"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(self.message if message is None else message)


class ReservationError(ParkingReservationError):
    message = "Something went wrong with your reservation"


class SpotOutOfServiceError(ReservationError):
    message = "Wanted spot is out of service right now"


class SpotAlreadyBookedError(ReservationError):
    message = "Wanted spot is already booked in that period of time"


class ReversedBookingTimeError(ReservationError):
    message = "Wanted booking time is reversed"


class BookingTimeInPastError(ReservationError):
    message = "Wanted booking time is in past"


class BookingNotFoundError(ReservationError):
    message = "Wanted booking is not found in that service"


class SpotIsNotInGivenLotError(ReservationError):
    message = "Wanted spot is not in given lot"


class LotIsNotOpenError(ReservationError):
    message = "Wanted lot is not open"


class InvalidTimezoneError(ReservationError):
    message = "Invalid booking time or timezone"


class ParkingLotError(ParkingReservationError):
    message = "Something went wrong with your parking lot"


class DuplicateSpotNumberError(ParkingLotError):
    message = "Spot with given number already exists"


class LotCollectionError(ParkingReservationError):
    message = "Something went wrong with your parking lot collection"


class DuplicateLotNumberError(LotCollectionError):
    message = "Lot with given number already exists"


class LotNotFoundError(LotCollectionError):
    message = "Lot number is absent"


class LoaderError(ParkingReservationError):
    message = "Something went wrong with loader"


class KeyMissingError(LoaderError):
    message = "Key is missing"


class LotDescriptionKeyValueError(LoaderError):
    message = "Lot key value is not valid"


class InvalidEnumError(LoaderError):
    message = "Enum value wasn't found"


class InvalidTimezoneKeyError(LoaderError):
    message = "Invalid timezone key value"


class BookingCancellationError(ReservationError):
    message = "Something went wrong with booking cancellation"
