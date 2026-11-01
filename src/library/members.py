"""Members: the people allowed to borrow books."""

from dataclasses import dataclass

from library.errors import DuplicateError, NotFoundError


@dataclass
class Member:
    """A library member. Inactive members cannot borrow."""

    member_id: str
    name: str
    email: str
    active: bool = True


class MemberRegistry:
    """In-memory collection of members."""

    def __init__(self) -> None:
        self._members: dict[str, Member] = {}

    def register(self, member_id: str, name: str, email: str) -> Member:
        """Register a new active member. The id must be new and the email must contain '@'."""
        if "@" not in email:
            raise ValueError("email must contain '@'")
        if member_id in self._members:
            raise DuplicateError(f"member {member_id} already exists")
        member = Member(member_id, name, email)
        self._members[member_id] = member
        return member

    def get_member(self, member_id: str) -> Member:
        """Return the member with this id or raise NotFoundError."""
        try:
            return self._members[member_id]
        except KeyError:
            raise NotFoundError(f"member {member_id} not found") from None

    def deactivate(self, member_id: str) -> Member:
        """Mark a member inactive so they can no longer borrow."""
        member = self.get_member(member_id)
        member.active = False
        return member

    def is_active(self, member_id: str) -> bool:
        """Return True when the member exists and is active."""
        member = self._members.get(member_id)
        return member is not None and member.active
