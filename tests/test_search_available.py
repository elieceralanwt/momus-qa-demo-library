from datetime import date

import pytest

from library.catalog import Catalog
from library.fines import FineLedger
from library.loans import LoanService
from library.members import MemberRegistry

TODAY = date(2026, 1, 5)


@pytest.fixture
def setup():
    catalog = Catalog()
    members = MemberRegistry()
    catalog.add_book("111", "Dune", "Frank Herbert", copies=1)
    catalog.add_book("222", "Dune Messiah", "Frank Herbert", copies=1)
    members.register("m-001", "Ana", "ana@example.com")
    return LoanService(catalog, members, FineLedger())


def test_ac1_hide_a_title_whose_copies_are_all_lent(setup):
    setup.checkout("111", "m-001", TODAY)
    result = setup.search_available("dune")
    assert [b.title for b in result] == ["Dune Messiah"]


def test_ac2_show_a_title_again_after_it_is_returned(setup):
    loan = setup.checkout("111", "m-001", TODAY)
    setup.return_book(loan.loan_id, TODAY)
    assert len(setup.search_available("dune")) == 2


def test_ac3_no_matching_title(setup):
    assert setup.search_available("Neuromancer") == []
