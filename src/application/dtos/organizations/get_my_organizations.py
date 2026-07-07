from dataclasses import dataclass


@dataclass
class GetMyOrganizationsRequest:
    user_id: str


@dataclass
class OrganizationWithRoleDTO:
    id: str
    name: str
    slug: str
    role: str
