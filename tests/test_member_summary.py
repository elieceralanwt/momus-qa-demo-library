from datetime import date
from decimal import Decimal

import pytest

from library.catalog import Catalog
from library.errors import NotFoundError
from library.fines import FineLedger
from library.loans import MAX_ACTIVE_LOANS, LoanService
from library.members import MemberRegistry

TODAY = date(2026, 1, 5)


@pytest.fixture
def setup():
    catalog = Catalog()
    members = MemberRegistry()
    fines = FineLedger()
    for i in range(MAX_ACTIVE_LOANS):
        catalog.add_book(f"isbn-{i}", f"Book {i}", "Author")
    members.register("m-001", "Ana", "ana@example.com")
    return members, fines, LoanService(catalog, members, fines)


def test_ac1_summary_of_an_active_member(setup):
    _, fines, loans = setup
    loans.checkout("isbn-0", "m-001", TODAY)
    loans.checkout("isbn-1", "m-001", TODAY)
    fines.add_fine("m-001", Decimal("3.00"))
    summary = loans.member_summary("m-001")
    assert summary.active is True
    assert summary.active_loans == 2
    assert summary.fines_owed == Decimal("3.00")
    assert summary.books_allowed == 3


def test_ac2_member_at_the_loan_limit(setup):
    *_, loans = setup
    for i in range(MAX_ACTIVE_LOANS):
        loans.checkout(f"isbn-{i}", "m-001", TODAY)
    summary = loans.member_summary("m-001")
    assert summary.active_loans == 5
    assert summary.books_allowed == 0


def test_ac3_inactive_member(setup):
    members, _, loans = setup
    members.register("m-002", "Luis", "luis@example.com")
    members.deactivate("m-002")
    summary = loans.member_summary("m-002")
    assert summary.active is False
    assert summary.active_loans == 0
    assert summary.books_allowed == 0


def test_ac4_unknown_member(setup):
    *_, loans = setup
    with pytest.raises(NotFoundError, match="member m-999 not found"):
        loans.member_summary("m-999")
