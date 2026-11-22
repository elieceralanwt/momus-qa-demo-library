from decimal import Decimal

from library.fines import FineLedger


def test_ac1_waive_a_balance():
    ledger = FineLedger()
    ledger.add_fine("m-002", Decimal("7.50"))
    assert ledger.waive("m-002") == Decimal("7.50")
    assert ledger.balance("m-002") == Decimal("0.00")


def test_ac2_waive_when_nothing_is_owed():
    ledger = FineLedger()
    assert ledger.waive("m-003") == Decimal("0.00")
    assert ledger.balance("m-003") == Decimal("0.00")


def test_ac3_other_members_are_not_affected():
    ledger = FineLedger()
    ledger.add_fine("m-002", Decimal("7.50"))
    ledger.add_fine("m-004", Decimal("2.00"))
    ledger.waive("m-002")
    assert ledger.balance("m-004") == Decimal("2.00")
