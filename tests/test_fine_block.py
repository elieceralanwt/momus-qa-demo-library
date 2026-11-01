from datetime import date, timedelta
from decimal import Decimal

import pytest

from library.errors import LoanNotAllowedError
from library.loans import LOAN_DAYS

DAY = date(2026, 10, 31)


def test_checkout_refused_at_threshold(world):  # @AC-1
    _, _, fines, loans = world
    fines.add_fine("m1", Decimal("5.00"))
    with pytest.raises(LoanNotAllowedError, match="member has unpaid fines"):
        loans.checkout("111", "m1", DAY)
    assert loans.active_loans("m1") == []


def test_checkout_allowed_below_threshold(world):  # @AC-2
    _, _, fines, loans = world
    fines.add_fine("m1", Decimal("4.75"))
    loan = loans.checkout("111", "m1", DAY)
    assert loan.due_date == DAY + timedelta(days=LOAN_DAYS)


def test_checkout_allowed_after_fines_paid(world):  # @AC-3
    _, _, fines, loans = world
    fines.add_fine("m1", Decimal("6.00"))
    fines.pay("m1", Decimal("6.00"))
    loan = loans.checkout("111", "m1", DAY)
    assert loan.due_date == date(2026, 11, 14)
