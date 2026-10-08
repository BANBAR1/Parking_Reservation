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


class LotCollectionError(ParkingLotError):
    message = "Something went wrong with your parking lot collection"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(self.message if message is None else message)


class DuplicateLotNumberError(LotCollectionError):
    message = "Lot with given number already exists"


class LotNotFoundError(LotCollectionError):
    message = "Lot number is absent"


class LoaderError(Exception):
    message = "Something went wrong with loader"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(self.message if message is None else message)


class KeyMissingError(LoaderError):
    message = "Key is missing"


class LotDescriptionKeyTypeError(LoaderError):
    message = "Lot key type is not valid"


class InvalidEnumError(LoaderError):
    message = "Enum value wasn't found"
