from datetime import date
from decimal import Decimal

import pytest

from library.errors import ReservationError
from library.fines import FineLedger, calculate_fine, days_late
from library.reservations import ReservationQueue

DUE = date(2026, 2, 1)


def test_days_late_is_never_negative():
    assert days_late(DUE, date(2026, 1, 20)) == 0
    assert days_late(DUE, date(2026, 2, 4)) == 3


def test_calculate_fine():
    assert calculate_fine(DUE, DUE) == 0
    assert calculate_fine(DUE, date(2026, 2, 5)) == Decimal("1.00")


def test_ledger_add_and_pay():
    ledger = FineLedger()
    ledger.add_fine("m1", Decimal("2.00"))
    assert ledger.pay("m1", Decimal("0.50")) == Decimal("1.50")
    with pytest.raises(ValueError):
        ledger.pay("m1", Decimal("5.00"))
    with pytest.raises(ValueError):
        ledger.add_fine("m1", Decimal(-1))


def test_reservation_queue_order():
    q = ReservationQueue()
    assert q.reserve("1", "a") == 1
    assert q.reserve("1", "b") == 2
    assert q.next_in_line("1") == "a"
    assert q.pop_next("1") == "a"
    assert q.position("1", "b") == 1


def test_reservation_rejects_duplicates_and_unknown_cancel():
    q = ReservationQueue()
    q.reserve("1", "a")
    with pytest.raises(ReservationError):
        q.reserve("1", "a")
    with pytest.raises(ReservationError):
        q.cancel("1", "zzz")
    q.cancel("1", "a")
    assert q.position("1", "a") is None
    assert q.next_in_line("1") is None
