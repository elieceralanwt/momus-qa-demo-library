from library.reservations import ReservationQueue

ISBN = "978-0-13-110362-7"


def test_ac1_list_members_in_reservation_order():
    q = ReservationQueue()
    for m in ("m-003", "m-004", "m-005"):
        q.reserve(ISBN, m)
    assert q.waiting_list(ISBN) == ["m-003", "m-004", "m-005"]


def test_ac2_title_nobody_reserved():
    assert ReservationQueue().waiting_list("978-0-596-51774-8") == []


def test_ac3_cancelled_reservation_leaves_the_list():
    q = ReservationQueue()
    for m in ("m-003", "m-004", "m-005"):
        q.reserve(ISBN, m)
    q.cancel(ISBN, "m-004")
    assert q.waiting_list(ISBN) == ["m-003", "m-005"]


def test_waiting_list_is_a_copy():
    q = ReservationQueue()
    q.reserve(ISBN, "m-003")
    q.waiting_list(ISBN).append("m-009")
    assert q.waiting_list(ISBN) == ["m-003"]
