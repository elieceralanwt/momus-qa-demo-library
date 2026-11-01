"""Loans: checking books out, returning them and renewing them."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from itertools import count

from library.catalog import Catalog
from library.errors import LoanNotAllowedError, NotFoundError
from library.fines import FineLedger, calculate_fine
from library.members import MemberRegistry

LOAN_DAYS = 14
RENEWAL_DAYS = 14
MAX_ACTIVE_LOANS = 5


@dataclass
class Loan:
    """One copy of a book lent to a member."""

    loan_id: int
    isbn: str
    member_id: str
    borrowed_on: date
    due_date: date
    returned_on: date | None = None
    renewals: int = 0

    @property
    def is_active(self) -> bool:
        """True while the book has not been returned."""
        return self.returned_on is None


class LoanService:
    """Applies the lending rules on top of the catalog, members and fines."""

    def __init__(self, catalog: Catalog, members: MemberRegistry, fines: FineLedger) -> None:
        self._catalog = catalog
        self._members = members
        self._fines = fines
        self._loans: dict[int, Loan] = {}
        self._ids = count(1)

    def copies_available(self, isbn: str) -> int:
        """Return how many copies of a title are not currently lent out."""
        book = self._catalog.get_book(isbn)
        lent = sum(1 for loan in self._loans.values() if loan.isbn == isbn and loan.is_active)
        return book.copies - lent

    def active_loans(self, member_id: str) -> list[Loan]:
        """Return the member's loans that have not been returned."""
        return [l for l in self._loans.values() if l.member_id == member_id and l.is_active]

    def checkout(self, isbn: str, member_id: str, today: date) -> Loan:
        """Lend a copy for LOAN_DAYS days.

        Rules: the member must be active, under MAX_ACTIVE_LOANS, and a copy must be free.
        Known gap: unpaid fines do not block a checkout yet.
        """
        self._members.get_member(member_id)
        if not self._members.is_active(member_id):
            raise LoanNotAllowedError("member is not active")
        if len(self.active_loans(member_id)) >= MAX_ACTIVE_LOANS:
            raise LoanNotAllowedError("member has reached the active loan limit")
        if self.copies_available(isbn) < 1:
            raise LoanNotAllowedError("no copies available")
        loan = Loan(next(self._ids), isbn, member_id, today, today + timedelta(days=LOAN_DAYS))
        self._loans[loan.loan_id] = loan
        return loan

    def get_loan(self, loan_id: int) -> Loan:
        """Return a loan by id or raise NotFoundError."""
        try:
            return self._loans[loan_id]
        except KeyError:
            raise NotFoundError(f"loan {loan_id} not found") from None

    def return_book(self, loan_id: int, today: date) -> Decimal:
        """Close a loan, charge any late fee to the member's ledger and return the fee."""
        loan = self.get_loan(loan_id)
        if not loan.is_active:
            raise LoanNotAllowedError("loan is already returned")
        loan.returned_on = today
        fee = calculate_fine(loan.due_date, today)
        if fee > 0:
            self._fines.add_fine(loan.member_id, fee)
        return fee

    def renew(self, loan_id: int, today: date) -> Loan:
        """Extend the due date by RENEWAL_DAYS. Overdue loans cannot be renewed.

        Known gap: there is no limit on how many times a loan can be renewed.
        """
        loan = self.get_loan(loan_id)
        if not loan.is_active:
            raise LoanNotAllowedError("loan is already returned")
        if is_overdue(loan, today):
            raise LoanNotAllowedError("overdue loans cannot be renewed")
        loan.due_date += timedelta(days=RENEWAL_DAYS)
        loan.renewals += 1
        return loan


def is_overdue(loan: Loan, today: date) -> bool:
    """True when the loan is still active and past its due date."""
    return loan.is_active and today > loan.due_date
