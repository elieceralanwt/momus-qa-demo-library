from datetime import date

import pytest

from library.catalog import Catalog
from library.errors import LoanNotAllowedError
from library.fines import FineLedger
from library.loans import LoanService
from library.members import MemberRegistry
from library.reservations import ReservationQueue

ISBN = "978-0-13-110362-7"
TODAY = date(2026, 10, 31)


@pytest.fixture
def setup():
    catalog = Catalog()
    members = MemberRegistry()
    catalog.add_book(ISBN, "The C Programming Language", "Kernighan", copies=1)
    for m in ("m-003", "m-004"):
        members.register(m, m, f"{m}@example.com")
    queue = ReservationQueue()
    return LoanService(catalog, members, FineLedger(), queue), queue


def test_ac1_refuse_member_not_first_in_line(setup):
    service, queue = setup
    queue.reserve(ISBN, "m-003")
    queue.reserve(ISBN, "m-004")
    with pytest.raises(LoanNotAllowedError, match="book is reserved for another member"):
        service.checkout(ISBN, "m-004", TODAY)


def test_ac2_lend_to_first_in_line_and_remove_from_queue(setup):
    service, queue = setup
    queue.reserve(ISBN, "m-003")
    queue.reserve(ISBN, "m-004")
    loan = service.checkout(ISBN, "m-003", TODAY)
    assert loan.due_date == date(2026, 11, 14)
    assert queue.next_in_line(ISBN) == "m-004"


def test_ac3_lend_freely_when_nobody_queued(setup):
    service, _ = setup
    loan = service.checkout(ISBN, "m-004", TODAY)
    assert loan.due_date == date(2026, 11, 14)
