from datetime import datetime

from pydantic import BaseModel


class AppointmentCreateRequest(BaseModel):
    organization_id: str
    employee_id: str
    client_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
    notes: str | None = None


class AppointmentUpdateRequest(BaseModel):
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    notes: str | None = None


class AppointmentResponse(BaseModel):
    id: str
    organization_id: str
    employee_id: str
    client_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
    status: str
    notes: str | None
