from dataclasses import dataclass
from datetime import datetime


@dataclass
class CreateAppointmentRequest:
    organization_id: str
    owner_user_id: str
    employee_id: str
    client_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
    notes: str | None = None


@dataclass
class CreateAppointmentResponse:
    id: str
    organization_id: str
    employee_id: str
    client_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
    status: str
    notes: str | None
