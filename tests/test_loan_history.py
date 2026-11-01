from datetime import date

import pytest

from library.errors import NotFoundError


def test_lists_loans_newest_first(world):  # @AC-1
    catalog, members, fines, loans = world
    catalog.add_book("222", "Emma", "Jane Austen", copies=1)
    loans.checkout("111", "m1", date(2026, 9, 1))
    loans.checkout("222", "m1", date(2026, 10, 1))
    report = loans.history("m1", date(2026, 10, 2))
    assert [entry.isbn for entry in report] == ["222", "111"]


def test_marks_late_return(world):  # @AC-2
    _, _, _, loans = world
    loan = loans.checkout("111", "m1", date(2026, 9, 17))  # due 2026-10-01
    loans.return_book(loan.loan_id, date(2026, 10, 5))
    (entry,) = loans.history("m1", date(2026, 10, 6))
    assert entry.days_late == 4


def test_on_time_return_is_not_late(world):
    _, _, _, loans = world
    loan = loans.checkout("111", "m1", date(2026, 9, 17))
    loans.return_book(loan.loan_id, date(2026, 10, 1))
    assert loans.history("m1", date(2026, 10, 6))[0].days_late == 0


def test_member_without_loans_has_empty_report(world):  # @AC-3
    _, _, _, loans = world
    assert loans.history("m2", date(2026, 10, 6)) == []


def test_unknown_member_raises(world):
    _, _, _, loans = world
    with pytest.raises(NotFoundError):
        loans.history("nobody", date(2026, 10, 6))
