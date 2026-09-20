from builtins import Exception


class ReservationError(Exception):
    def __init__(self, message: str = "Something went wrong with your reservation") -> None:
        self.message = message
        super().__init__(self.message)


class SpotOutOfServiceError(ReservationError):
    def __init__(self, message: str = "Wanted spot is out of service right now") -> None:
        super().__init__(message)


class SpotAlreadyBookedError(ReservationError):
    def __init__(
        self, message: str = "Wanted spot is already booked in that period of time"
    ) -> None:
        super().__init__(message)


class ReversedBookingTimeError(ReservationError):
    def __init__(self, message: str = "Wanted booking time is reversed") -> None:
        super().__init__(message)


class BookingTimeInPastError(ReservationError):
    def __init__(self, message: str = "Wanted booking time is in past") -> None:
        super().__init__(message)


class BookingNotFoundError(ReservationError):
    def __init__(self, message: str = "Wanted booking is not found in that service") -> None:
        super().__init__(message)


class SpotIsNotInGivenLotError(ReservationError):
    def __init__(self, message: str = "Wanted spot is not in given lot") -> None:
        super().__init__(message)
