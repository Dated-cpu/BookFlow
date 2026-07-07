from dataclasses import dataclass


@dataclass
class CancelAppointmentRequest:
    appointment_id: str
    user_id: str


@dataclass
class CancelAppointmentResponse:
    id: str
    status: str
