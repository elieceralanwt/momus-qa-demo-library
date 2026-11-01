"""Fines: late fees for overdue returns and a per-member ledger."""

from collections import defaultdict
from datetime import date
from decimal import Decimal

DAILY_RATE = Decimal("0.25")


def days_late(due_date: date, returned_on: date) -> int:
    """Return the whole days between the due date and the return (0 if on time)."""
    return max((returned_on - due_date).days, 0)


def calculate_fine(due_date: date, returned_on: date) -> Decimal:
    """Return the late fee: DAILY_RATE per day late.

    Known gap: the fee is not capped yet.
    """
    return DAILY_RATE * days_late(due_date, returned_on)


class FineLedger:
    """Tracks the unpaid fine balance of each member."""

    def __init__(self) -> None:
        self._balances: defaultdict[str, Decimal] = defaultdict(Decimal)

    def add_fine(self, member_id: str, amount: Decimal) -> Decimal:
        """Add a fine to the member's balance and return the new balance."""
        if amount < 0:
            raise ValueError("amount must not be negative")
        self._balances[member_id] += amount
        return self._balances[member_id]

    def pay(self, member_id: str, amount: Decimal) -> Decimal:
        """Reduce the balance by `amount`, which cannot exceed what is owed."""
        if amount <= 0:
            raise ValueError("payment must be positive")
        if amount > self._balances[member_id]:
            raise ValueError("payment exceeds the outstanding balance")
        self._balances[member_id] -= amount
        return self._balances[member_id]

    def balance(self, member_id: str) -> Decimal:
        """Return the unpaid balance of a member (0 if none)."""
        return self._balances.get(member_id, Decimal(0))
