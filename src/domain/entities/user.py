from dataclasses import dataclass
from datetime import UTC, datetime

from src.domain.base import BaseEntity


def _validate_email(email: str) -> None:
    if not email or "@" not in email:
        raise ValueError(f"Invalid email: {email!r}")


@dataclass(kw_only=True)
class User(BaseEntity):
    email: str
    hashed_password: str
    is_active: bool = True

    def change_email(self, new_email: str) -> None:
        _validate_email(new_email)
        self.email = new_email
        self.updated_at = datetime.now(UTC)
