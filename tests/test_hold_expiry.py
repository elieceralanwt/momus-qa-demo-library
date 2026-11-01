from datetime import date

from library.reservations import HOLD_DAYS, ReservationQueue

ISBN = "978-0-13-110362-7"
START = date(2026, 10, 1)


def make_queue() -> ReservationQueue:
    queue = ReservationQueue()
    queue.reserve(ISBN, "m-003")
    queue.reserve(ISBN, "m-004")
    queue.start_hold(ISBN, START)
    return queue


def test_hold_still_valid_after_three_days():  # @AC-1
    queue = make_queue()
    assert queue.expire_holds(ISBN, date(2026, 10, 4)) == []
    assert queue.next_in_line(ISBN) == "m-003"


def test_hold_expires_after_three_days():  # @AC-2
    queue = make_queue()
    assert queue.expire_holds(ISBN, date(2026, 10, 5)) == ["m-003"]
    assert queue.position(ISBN, "m-003") is None


def test_next_member_moves_up_when_hold_expires():  # @AC-3
    queue = make_queue()
    queue.expire_holds(ISBN, date(2026, 10, 5))
    assert queue.next_in_line(ISBN) == "m-004"
    assert queue.hold_expires_on(ISBN) == date(2026, 10, 8)


def test_no_hold_running_means_nothing_expires():
    queue = ReservationQueue()
    queue.reserve(ISBN, "m-003")
    assert queue.expire_holds(ISBN, date(2030, 1, 1)) == []
    assert queue.hold_expires_on(ISBN) is None


def test_cancel_front_member_clears_hold():
    queue = make_queue()
    queue.cancel(ISBN, "m-003")
    assert queue.hold_expires_on(ISBN) is None
    assert HOLD_DAYS == 3
