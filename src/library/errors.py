"""Domain errors raised by the library modules."""


class LibraryError(Exception):
    """Base class for all business-rule violations."""


class NotFoundError(LibraryError):
    """A book, member or loan does not exist."""


class DuplicateError(LibraryError):
    """An entity with the same identifier already exists."""


class LoanNotAllowedError(LibraryError):
    """A checkout or renewal breaks a lending rule."""


class ReservationError(LibraryError):
    """A reservation request breaks a reservation rule."""
