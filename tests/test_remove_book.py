import pytest

from library.catalog import Catalog
from library.errors import NotFoundError

ISBN = "978-0-13-110362-7"


def test_ac1_remove_existing_title():
    c = Catalog()
    c.add_book(ISBN, "The C Programming Language", "Kernighan")
    c.remove_book(ISBN)
    assert c.search("C Programming") == []


def test_ac2_refuse_unknown_title():
    c = Catalog()
    with pytest.raises(NotFoundError, match="book 000-0-00-000000-0 not found"):
        c.remove_book("000-0-00-000000-0")


def test_ac3_add_title_again_after_removal():
    c = Catalog()
    c.add_book(ISBN, "The C Programming Language", "Kernighan")
    c.remove_book(ISBN)
    c.add_book(ISBN, "The C Programming Language", "Kernighan", copies=2)
    assert c.get_book(ISBN).copies == 2
