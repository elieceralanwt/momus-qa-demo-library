from datetime import date

import pytest

from library.catalog import Catalog
from library.errors import LoanNotAllowedError, NotFoundError
from library.fines import FineLedger
from library.loans import LoanService
from library.members import MemberRegistry


def make_service():
    catalog = Catalog()
    members = MemberRegistry()
    catalog.add_book("111", "Dune", "Frank Herbert")
    members.register("m-001", "Ana", "ana@example.com")
    members.register("m-002", "Luis", "luis@example.com")
    return members, LoanService(catalog, members, FineLedger())


def test_ac1_refuse_while_a_loan_is_active():
    members, s = make_service()
    s.checkout("111", "m-001", date(2026, 1, 5))
    with pytest.raises(LoanNotAllowedError, match="member has active loans"):
        s.deactivate_member("m-001")
    assert members.is_active("m-001")


def test_ac2_deactivate_after_the_book_is_returned():
    members, s = make_service()
    loan = s.checkout("111", "m-001", date(2026, 1, 5))
    s.return_book(loan.loan_id, date(2026, 1, 10))
    s.deactivate_member("m-001")
    assert not members.is_active("m-001")


def test_ac3_deactivate_a_member_who_never_borrowed():
    members, s = make_service()
    s.deactivate_member("m-002")
    assert not members.is_active("m-002")


def test_ac4_refuse_an_unknown_member():
    _, s = make_service()
    with pytest.raises(NotFoundError, match="member m-999 not found"):
        s.deactivate_member("m-999")
