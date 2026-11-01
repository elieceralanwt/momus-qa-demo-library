"""Reservations: a first-come, first-served queue of members waiting for a title."""

from collections import defaultdict, deque
from datetime import date, timedelta

from library.errors import ReservationError

HOLD_DAYS = 3


class ReservationQueue:
    """Holds the waiting list for each ISBN.

    A hold starts when the book becomes available for the member at the front of the
    queue and lasts HOLD_DAYS days. Known gap: checkout does not consult the queue yet.
    """

    def __init__(self) -> None:
        self._queues: defaultdict[str, deque[str]] = defaultdict(deque)
        self._hold_started: dict[str, date] = {}

    def reserve(self, isbn: str, member_id: str) -> int:
        """Add a member to the queue and return their 1-based position."""
        queue = self._queues[isbn]
        if member_id in queue:
            raise ReservationError("member already has a reservation for this book")
        queue.append(member_id)
        return len(queue)

    def cancel(self, isbn: str, member_id: str) -> None:
        """Remove a member from the queue."""
        queue = self._queues[isbn]
        if member_id not in queue:
            raise ReservationError("member has no reservation for this book")
        if queue[0] == member_id:
            self._hold_started.pop(isbn, None)
        queue.remove(member_id)

    def position(self, isbn: str, member_id: str) -> int | None:
        """Return the member's 1-based position, or None if not queued."""
        queue = self._queues.get(isbn, deque())
        return queue.index(member_id) + 1 if member_id in queue else None

    def next_in_line(self, isbn: str) -> str | None:
        """Return the member at the front of the queue without removing them."""
        queue = self._queues.get(isbn)
        return queue[0] if queue else None

    def pop_next(self, isbn: str) -> str | None:
        """Remove and return the member at the front of the queue."""
        queue = self._queues.get(isbn)
        if not queue:
            return None
        self._hold_started.pop(isbn, None)
        return queue.popleft()

    def start_hold(self, isbn: str, started_on: date) -> str | None:
        """Start the hold of the member at the front of the queue and return them."""
        member_id = self.next_in_line(isbn)
        if member_id is not None:
            self._hold_started[isbn] = started_on
        return member_id

    def hold_expires_on(self, isbn: str) -> date | None:
        """Return the last day the current hold is valid, or None if no hold is running."""
        started = self._hold_started.get(isbn)
        return started + timedelta(days=HOLD_DAYS) if started else None

    def expire_holds(self, isbn: str, today: date) -> list[str]:
        """Drop the front member while their hold is over and return who was removed.

        A hold is valid through its HOLD_DAYS-th day. When it expires, the next member
        moves up and their hold starts today.
        """
        removed: list[str] = []
        while (last_day := self.hold_expires_on(isbn)) is not None and today > last_day:
            removed.append(self.pop_next(isbn) or "")
            self.start_hold(isbn, today)
        return removed
