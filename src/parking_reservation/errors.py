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
