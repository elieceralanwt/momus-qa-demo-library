"""Reservations: a first-come, first-served queue of members waiting for a title."""

from collections import defaultdict, deque

from library.errors import ReservationError


class ReservationQueue:
    """Holds the waiting list for each ISBN.

    Known gaps: holds never expire, and checkout does not consult the queue yet.
    """

    def __init__(self) -> None:
        self._queues: defaultdict[str, deque[str]] = defaultdict(deque)

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
        return queue.popleft() if queue else None
