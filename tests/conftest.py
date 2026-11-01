from datetime import date

import pytest

from library.catalog import Catalog
from library.fines import FineLedger
from library.loans import LoanService
from library.members import MemberRegistry

TODAY = date(2026, 1, 5)


@pytest.fixture
def world():
    catalog = Catalog()
    members = MemberRegistry()
    fines = FineLedger()
    catalog.add_book("111", "Dune", "Frank Herbert", copies=1)
    members.register("m1", "Ana", "ana@example.com")
    members.register("m2", "Luis", "luis@example.com")
    return catalog, members, fines, LoanService(catalog, members, fines)
