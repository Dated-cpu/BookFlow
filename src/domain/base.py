import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class BaseEntity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
