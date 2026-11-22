import pytest

from library.catalog import Catalog
from library.errors import NotFoundError, ReservationError
from library.members import MemberRegistry
from library.reservations import ReservationQueue, ReservationService

ISBN = "978-0-13-110362-7"


@pytest.fixture
def setup():
    catalog = Catalog()
    members = MemberRegistry()
    queue = ReservationQueue()
    catalog.add_book(ISBN, "Clean Code", "Robert Martin")
    members.register("m-001", "Ana", "ana@example.com")
    return catalog, members, queue, ReservationService(catalog, members, queue)


def test_ac1_reserve_with_known_member_and_title(setup):
    *_, service = setup
    assert service.reserve(ISBN, "m-001") == 1


def test_ac2_refuse_unknown_title(setup):
    *_, service = setup
    with pytest.raises(NotFoundError, match="book 000-0-00-000000-0 not found"):
        service.reserve("000-0-00-000000-0", "m-001")


def test_ac3_refuse_unknown_member(setup):
    *_, service = setup
    with pytest.raises(NotFoundError, match="member m-999 not found"):
        service.reserve(ISBN, "m-999")


def test_ac4_refuse_inactive_member(setup):
    _, members, queue, service = setup
    members.register("m-002", "Luis", "luis@example.com")
    members.deactivate("m-002")
    with pytest.raises(ReservationError, match="member is not active"):
        service.reserve(ISBN, "m-002")
    assert queue.next_in_line(ISBN) is None
