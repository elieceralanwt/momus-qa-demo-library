from datetime import timedelta
from decimal import Decimal

import pytest

from conftest import TODAY
from library.errors import LoanNotAllowedError
from library.loans import LOAN_DAYS, MAX_ACTIVE_LOANS, RENEWAL_DAYS, is_overdue


def test_checkout_sets_due_date(world):
    *_, loans = world
    loan = loans.checkout("111", "m1", TODAY)
    assert loan.due_date == TODAY + timedelta(days=LOAN_DAYS)
    assert loans.copies_available("111") == 0


def test_checkout_fails_without_copies(world):
    *_, loans = world
    loans.checkout("111", "m1", TODAY)
    with pytest.raises(LoanNotAllowedError):
        loans.checkout("111", "m2", TODAY)


def test_checkout_fails_for_inactive_member(world):
    _, members, _, loans = world
    members.deactivate("m1")
    with pytest.raises(LoanNotAllowedError):
        loans.checkout("111", "m1", TODAY)


def test_checkout_respects_active_loan_limit(world):
    catalog, _, _, loans = world
    for i in range(MAX_ACTIVE_LOANS):
        catalog.add_book(f"b{i}", "T", "A")
        loans.checkout(f"b{i}", "m1", TODAY)
    with pytest.raises(LoanNotAllowedError):
        loans.checkout("111", "m1", TODAY)


def test_on_time_return_has_no_fee(world):
    _, _, fines, loans = world
    loan = loans.checkout("111", "m1", TODAY)
    assert loans.return_book(loan.loan_id, TODAY) == 0
    assert fines.balance("m1") == 0
    assert loans.copies_available("111") == 1


def test_late_return_charges_fine(world):
    _, _, fines, loans = world
    loan = loans.checkout("111", "m1", TODAY)
    late = loan.due_date + timedelta(days=4)
    assert loans.return_book(loan.loan_id, late) == Decimal("1.00")
    assert fines.balance("m1") == Decimal("1.00")


def test_cannot_return_twice(world):
    *_, loans = world
    loan = loans.checkout("111", "m1", TODAY)
    loans.return_book(loan.loan_id, TODAY)
    with pytest.raises(LoanNotAllowedError):
        loans.return_book(loan.loan_id, TODAY)


def test_renew_extends_due_date(world):
    *_, loans = world
    loan = loans.checkout("111", "m1", TODAY)
    original = loan.due_date
    loans.renew(loan.loan_id, TODAY)
    assert loan.due_date == original + timedelta(days=RENEWAL_DAYS)
    assert loan.renewals == 1


def test_overdue_loan_cannot_be_renewed(world):
    *_, loans = world
    loan = loans.checkout("111", "m1", TODAY)
    with pytest.raises(LoanNotAllowedError):
        loans.renew(loan.loan_id, loan.due_date + timedelta(days=1))


def test_is_overdue(world):
    *_, loans = world
    loan = loans.checkout("111", "m1", TODAY)
    assert not is_overdue(loan, loan.due_date)
    assert is_overdue(loan, loan.due_date + timedelta(days=1))
