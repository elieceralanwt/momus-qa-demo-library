import pytest

from library.errors import ReservationError
from library.reservations import MAX_RESERVATIONS, ReservationQueue


@pytest.fixture
def queue():
    q = ReservationQueue()
    for isbn in ("111", "222", "333"):
        q.reserve(isbn, "m-001")
    return q


def test_ac1_refuse_a_fourth_reservation(queue):
    assert MAX_RESERVATIONS == 3
    with pytest.raises(ReservationError, match="member has reached the reservation limit"):
        queue.reserve("444", "m-001")
    assert queue.position("444", "m-001") is None


def test_ac2_cancelling_frees_a_slot(queue):
    queue.cancel("222", "m-001")
    assert queue.reserve("444", "m-001") == 1


def test_ac3_the_limit_is_per_member(queue):
    assert queue.reserve("111", "m-002") == 2
