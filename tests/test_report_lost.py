from datetime import date
from decimal import Decimal

import pytest

from library.catalog import Catalog
from library.errors import LoanNotAllowedError, NotFoundError
from library.fines import FineLedger
from library.loans import LoanService
from library.members import MemberRegistry

ISBN = "978-0-13-110362-7"


def make_service(copies=2):
    catalog = Catalog()
    members = MemberRegistry()
    fines = FineLedger()
    catalog.add_book(ISBN, "The C Programming Language", "Kernighan", copies=copies)
    members.register("m-001", "Ana", "ana@example.com")
    return catalog, fines, LoanService(catalog, members, fines)


def test_ac1_close_loan_and_remove_copy():
    catalog, _, s = make_service(copies=2)
    loan = s.checkout(ISBN, "m-001", date(2026, 1, 5))
    s.report_lost(loan.loan_id, date(2026, 1, 10))
    assert not s.get_loan(loan.loan_id).is_active
    assert catalog.get_book(ISBN).copies == 1


def test_ac2_charge_only_lost_book_fee():
    _, fines, s = make_service()
    loan = s.checkout(ISBN, "m-001", date(2026, 1, 5))
    assert loan.due_date == date(2026, 1, 19)
    s.report_lost(loan.loan_id, date(2026, 2, 1))
    assert fines.balance("m-001") == Decimal("15.00")


def test_ac3_refuse_loan_already_returned():
    _, _, s = make_service()
    loan = s.checkout(ISBN, "m-001", date(2026, 1, 5))
    s.return_book(loan.loan_id, date(2026, 1, 8))
    with pytest.raises(LoanNotAllowedError, match="loan is already returned"):
        s.report_lost(loan.loan_id, date(2026, 1, 10))


def test_ac4_refuse_unknown_loan():
    _, _, s = make_service()
    with pytest.raises(NotFoundError, match="loan 99 not found"):
        s.report_lost(99, date(2026, 1, 10))
