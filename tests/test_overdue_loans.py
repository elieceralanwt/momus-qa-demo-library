from datetime import date

from library.catalog import Catalog
from library.fines import FineLedger
from library.loans import LoanService
from library.members import MemberRegistry


def make_service():
    catalog = Catalog()
    members = MemberRegistry()
    catalog.add_book("111", "Dune", "Frank Herbert", copies=3)
    members.register("m-001", "Ana", "ana@example.com")
    members.register("m-002", "Luis", "luis@example.com")
    return LoanService(catalog, members, FineLedger())


def test_ac1_list_overdue_loans_earliest_due_date_first():
    s = make_service()
    s.checkout("111", "m-002", date(2026, 1, 10))
    s.checkout("111", "m-001", date(2026, 1, 5))
    report = s.overdue_loans(date(2026, 2, 1))
    assert len(report) == 2
    assert report[0].member_id == "m-001"
    assert report[0].due_date == date(2026, 1, 19)


def test_ac2_returned_loans_are_not_listed():
    s = make_service()
    loan = s.checkout("111", "m-001", date(2026, 1, 5))
    s.return_book(loan.loan_id, date(2026, 1, 25))
    assert s.overdue_loans(date(2026, 2, 1)) == []


def test_ac3_loan_due_today_is_not_overdue():
    s = make_service()
    s.checkout("111", "m-001", date(2026, 1, 5))
    assert s.overdue_loans(date(2026, 1, 19)) == []
