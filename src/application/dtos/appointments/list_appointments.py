from dataclasses import dataclass
from datetime import datetime


@dataclass
class ListAppointmentsRequest:
    organization_id: str
    user_id: str


@dataclass
class ListAppointmentsItem:
    id: str
    organization_id: str
    employee_id: str
    client_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
    status: str
    notes: str | None
