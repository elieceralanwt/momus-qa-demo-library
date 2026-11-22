from datetime import date
from decimal import Decimal

from library.catalog import Catalog
from library.fines import FineLedger
from library.loans import LoanService
from library.members import MemberRegistry


def make_service():
    catalog = Catalog()
    members = MemberRegistry()
    fines = FineLedger()
    catalog.add_book("111", "Dune", "Frank Herbert", copies=2)
    members.register("m-001", "Ana", "ana@example.com")
    return fines, LoanService(catalog, members, fines)


def test_ac1_late_return_adds_an_entry():
    fines, s = make_service()
    loan = s.checkout("111", "m-001", date(2026, 1, 5))
    s.return_book(loan.loan_id, date(2026, 1, 23))
    statement = fines.statement("m-001")
    assert len(statement) == 1
    assert statement[0].amount == Decimal("1.00")
    assert statement[0].reason == "late return of loan 1"


def test_ac2_entries_accumulate_in_order():
    fines, s = make_service()
    first = s.checkout("111", "m-001", date(2026, 1, 5))
    second = s.checkout("111", "m-001", date(2026, 1, 5))
    s.return_book(first.loan_id, date(2026, 1, 23))
    s.return_book(second.loan_id, date(2026, 1, 27))
    assert [e.amount for e in fines.statement("m-001")] == [Decimal("1.00"), Decimal("2.00")]
    assert fines.balance("m-001") == Decimal("3.00")


def test_ac3_on_time_returns_leave_no_entries():
    fines, s = make_service()
    loan = s.checkout("111", "m-001", date(2026, 1, 5))
    s.return_book(loan.loan_id, date(2026, 1, 19))
    assert fines.statement("m-001") == []


def test_ac4_payments_do_not_remove_entries():
    fines = FineLedger()
    fines.add_fine("m-001", Decimal("1.00"))
    fines.pay("m-001", Decimal("1.00"))
    assert len(fines.statement("m-001")) == 1
    assert fines.balance("m-001") == Decimal("0.00")
