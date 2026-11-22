import pytest

from library.errors import NotFoundError
from library.members import MemberRegistry


@pytest.fixture
def registry():
    r = MemberRegistry()
    r.register("m-001", "Ana", "ana@example.com")
    return r


def test_ac1_change_email(registry):
    registry.update_email("m-001", "ana@newmail.org")
    assert registry.get_member("m-001").email == "ana@newmail.org"


def test_ac2_refuse_email_without_at_sign(registry):
    with pytest.raises(ValueError, match="email must contain '@'"):
        registry.update_email("m-001", "ana-newmail.org")
    assert registry.get_member("m-001").email == "ana@example.com"


def test_ac3_refuse_unknown_member(registry):
    with pytest.raises(NotFoundError, match="member m-999 not found"):
        registry.update_email("m-999", "x@example.com")
