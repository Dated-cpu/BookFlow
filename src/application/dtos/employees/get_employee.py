from dataclasses import dataclass


@dataclass
class GetEmployeeRequest:
    employee_id: str
    user_id: str
