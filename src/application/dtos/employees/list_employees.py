from dataclasses import dataclass


@dataclass
class ListEmployeesRequest:
    organization_id: str
    user_id: str
