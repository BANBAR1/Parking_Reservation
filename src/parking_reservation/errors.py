class ReservationError(Exception):
    message = "Something went wrong with your reservation"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(self.message if message is None else message)


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


class ParkingLotError(Exception):
    message = "Something went wrong with your parking lot"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(self.message if message is None else message)


class DuplicateSpotNumberError(ParkingLotError):
    message = "Spot with given number already exists"


class LoaderError(Exception):
    message = "Something went wrong with loader"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(self.message if message is None else message)


class KeyMissingError(LoaderError):
    message = "Key is missing"


class LotDescriptionError(LoaderError):
    message = "Lot description must be a JSON object"


class LotDescriptionKeyTypeError(LoaderError):
    message = "Lot key type is not valid"


class InvalidEnumError(LoaderError):
    message = "Enum value wasn't found"


class InvalidSpotStatusError(InvalidEnumError):
    message = "Spot status is not valid, expected: AVAILABLE or OUT_OF_SERVICE"


class InvalidSpotTypeError(InvalidEnumError):
    message = (
        "Spot type is not valid, expected: DISABLED, WORKERS, VISITORS, "
        "ELECTRIC_VEHICLES, MANAGEMENT, or GENERAL"
    )


class InvalidLocationTypeError(InvalidEnumError):
    message = (
        "Location type is not valid, expected: MALL, OFFICE, AIRPORT, HOSPITAL, or RESIDENTIAL"
    )


class InvalidLotStatusError(InvalidEnumError):
    message = "Lot status is not valid, expected: OPEN, CLOSED, or UNDER_MAINTENANCE"


class InvalidLotTypeError(InvalidEnumError):
    message = "Lot type is not valid, expected: PUBLIC or PRIVATE"
