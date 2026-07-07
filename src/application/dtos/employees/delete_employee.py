from dataclasses import dataclass


@dataclass
class DeleteEmployeeRequest:
    employee_id: str
    user_id: str
