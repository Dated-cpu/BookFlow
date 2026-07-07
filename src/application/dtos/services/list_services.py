from dataclasses import dataclass


@dataclass
class ListServicesRequest:
    organization_id: str
    user_id: str
