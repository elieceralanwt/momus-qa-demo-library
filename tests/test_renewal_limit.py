from datetime import timedelta

import pytest

from conftest import TODAY
from library.errors import LoanNotAllowedError
from library.loans import MAX_RENEWALS, RENEWAL_DAYS


def test_second_renewal_is_allowed(world):  # @AC-1
    *_, loans = world
    loan = loans.checkout("111", "m1", TODAY)
    loans.renew(loan.loan_id, TODAY)
    due_before = loan.due_date
    loans.renew(loan.loan_id, TODAY)
    assert loan.due_date == due_before + timedelta(days=RENEWAL_DAYS)
    assert loan.renewals == 2


def test_third_renewal_is_refused(world):  # @AC-2
    *_, loans = world
    loan = loans.checkout("111", "m1", TODAY)
    for _ in range(MAX_RENEWALS):
        loans.renew(loan.loan_id, TODAY)
    due_before = loan.due_date
    with pytest.raises(LoanNotAllowedError, match="renewal limit reached"):
        loans.renew(loan.loan_id, TODAY)
    assert loan.due_date == due_before
    assert loan.renewals == MAX_RENEWALS
