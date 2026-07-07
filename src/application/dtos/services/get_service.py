from dataclasses import dataclass


@dataclass
class GetServiceRequest:
    service_id: str
    user_id: str
