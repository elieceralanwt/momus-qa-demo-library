from datetime import date
from decimal import Decimal

import pytest

from library.catalog import Catalog
from library.errors import LoanNotAllowedError, NotFoundError
from library.fines import FineLedger
from library.loans import LoanService
from library.members import MemberRegistry


def make_service():
    catalog = Catalog()
    members = MemberRegistry()
    fines = FineLedger()
    catalog.add_book("111", "Dune", "Frank Herbert")
    members.register("m-001", "Ana", "ana@example.com")
    return LoanService(catalog, members, fines), fines


def test_ac1_preview_fee_for_late_loan():
    s, fines = make_service()
    loan = s.checkout("111", "m-001", date(2026, 1, 5))
    assert s.projected_fine(loan.loan_id, date(2026, 1, 23)) == Decimal("1.00")
    assert s.get_loan(loan.loan_id).is_active
    assert fines.balance("m-001") == Decimal("0.00")


def test_ac2_preview_on_due_date():
    s, _ = make_service()
    loan = s.checkout("111", "m-001", date(2026, 1, 5))
    assert s.projected_fine(loan.loan_id, date(2026, 1, 19)) == Decimal("0.00")


def test_ac3_refuse_preview_for_returned_loan():
    s, _ = make_service()
    loan = s.checkout("111", "m-001", date(2026, 1, 5))
    s.return_book(loan.loan_id, date(2026, 1, 20))
    with pytest.raises(LoanNotAllowedError, match="loan is already returned"):
        s.projected_fine(loan.loan_id, date(2026, 1, 23))


def test_ac4_refuse_preview_for_unknown_loan():
    s, _ = make_service()
    with pytest.raises(NotFoundError, match="loan 99 not found"):
        s.projected_fine(99, date(2026, 1, 23))
