import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum, auto

from src.domain.base import BaseEntity


class OrganizationRole(StrEnum):
    OWNER = auto()
    ADMIN = auto()
    MANAGER = auto()
    EMPLOYEE = auto()


@dataclass(kw_only=True)
class OrganizationMember(BaseEntity):
    user_id: uuid.UUID
    organization_id: uuid.UUID
    role: OrganizationRole

    def change_role(self, new_role: OrganizationRole) -> None:
        self.role = new_role
        self.updated_at = datetime.now(UTC)
