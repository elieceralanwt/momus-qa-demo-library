from datetime import date
from decimal import Decimal

from library.fines import MAX_FINE, calculate_fine

DUE = date(2026, 10, 1)


def test_fee_below_cap_is_unchanged():  # @AC-1
    assert calculate_fine(DUE, date(2026, 10, 11)) == Decimal("2.50")


def test_fee_above_cap_is_limited():  # @AC-2
    assert calculate_fine(DUE, date(2026, 12, 1)) == Decimal("10.00")


def test_fee_exactly_at_cap():  # @AC-3
    assert calculate_fine(DUE, date(2026, 11, 10)) == MAX_FINE == Decimal("10.00")
