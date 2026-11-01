"""Book catalog: which titles the library owns and how many copies."""

from dataclasses import dataclass

from library.errors import DuplicateError, NotFoundError


@dataclass
class Book:
    """A title identified by ISBN, with the number of physical copies owned."""

    isbn: str
    title: str
    author: str
    copies: int = 1


class Catalog:
    """In-memory collection of books."""

    def __init__(self) -> None:
        self._books: dict[str, Book] = {}

    def add_book(self, isbn: str, title: str, author: str, copies: int = 1) -> Book:
        """Add a new title. Copies must be at least 1 and the ISBN must be new."""
        if copies < 1:
            raise ValueError("copies must be at least 1")
        if isbn in self._books:
            raise DuplicateError(f"book {isbn} already exists")
        book = Book(isbn, title, author, copies)
        self._books[isbn] = book
        return book

    def get_book(self, isbn: str) -> Book:
        """Return the book with this ISBN or raise NotFoundError."""
        try:
            return self._books[isbn]
        except KeyError:
            raise NotFoundError(f"book {isbn} not found") from None

    def search(self, text: str) -> list[Book]:
        """Return books whose title or author contains `text` (case-insensitive)."""
        needle = text.strip().lower()
        return [
            b
            for b in self._books.values()
            if needle in b.title.lower() or needle in b.author.lower()
        ]

    def add_copies(self, isbn: str, count: int) -> Book:
        """Increase the number of copies of an existing title."""
        if count < 1:
            raise ValueError("count must be at least 1")
        book = self.get_book(isbn)
        book.copies += count
        return book
