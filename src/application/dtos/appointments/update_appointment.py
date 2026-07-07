from dataclasses import dataclass
from datetime import datetime


@dataclass
class UpdateAppointmentRequest:
    appointment_id: str
    user_id: str
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    notes: str | None = None


@dataclass
class UpdateAppointmentResponse:
    id: str
    organization_id: str
    employee_id: str
    client_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
    status: str
    notes: str | None
