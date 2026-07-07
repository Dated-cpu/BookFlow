from dataclasses import dataclass


@dataclass
class DeleteServiceRequest:
    service_id: str
    user_id: str
