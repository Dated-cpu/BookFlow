import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum, auto

from src.domain.base import BaseEntity


class AppointmentStatus(StrEnum):
    SCHEDULED = auto()
    CONFIRMED = auto()
    COMPLETED = auto()
    CANCELLED = auto()


@dataclass(kw_only=True)
class Appointment(BaseEntity):
    organization_id: uuid.UUID
    employee_id: uuid.UUID
    client_id: uuid.UUID
    service_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: str | None = None

    def __post_init__(self) -> None:
        if self.ends_at <= self.starts_at:
            raise ValueError("End time must be after start time")

    def reschedule(self, new_starts_at: datetime, new_ends_at: datetime) -> None:
        if new_ends_at <= new_starts_at:
            raise ValueError("End time must be after start time")
        if self.status in (AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED):
            raise ValueError(f"Cannot reschedule a {self.status.value} appointment")
        self.starts_at = new_starts_at
        self.ends_at = new_ends_at
        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        if self.status == AppointmentStatus.CANCELLED:
            raise ValueError("Appointment is already cancelled")
        if self.status == AppointmentStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed appointment")
        self.status = AppointmentStatus.CANCELLED
        self.updated_at = datetime.now(UTC)
