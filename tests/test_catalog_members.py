import pytest

from library.catalog import Catalog
from library.errors import DuplicateError, NotFoundError
from library.members import MemberRegistry


def test_add_and_search_books():
    c = Catalog()
    c.add_book("1", "Dune", "Frank Herbert")
    c.add_book("2", "Emma", "Jane Austen")
    assert [b.isbn for b in c.search("herbert")] == ["1"]


def test_duplicate_and_missing_book():
    c = Catalog()
    c.add_book("1", "Dune", "Frank Herbert")
    with pytest.raises(DuplicateError):
        c.add_book("1", "Dune", "Frank Herbert")
    with pytest.raises(NotFoundError):
        c.get_book("9")


def test_add_copies_validates_count():
    c = Catalog()
    c.add_book("1", "Dune", "Frank Herbert")
    assert c.add_copies("1", 2).copies == 3
    with pytest.raises(ValueError):
        c.add_copies("1", 0)


def test_register_and_deactivate_member():
    r = MemberRegistry()
    r.register("m1", "Ana", "ana@example.com")
    assert r.is_active("m1")
    r.deactivate("m1")
    assert not r.is_active("m1")
    assert not r.is_active("nobody")


def test_register_rejects_bad_email_and_duplicates():
    r = MemberRegistry()
    with pytest.raises(ValueError):
        r.register("m1", "Ana", "nope")
    r.register("m1", "Ana", "ana@example.com")
    with pytest.raises(DuplicateError):
        r.register("m1", "Ana", "ana@example.com")
