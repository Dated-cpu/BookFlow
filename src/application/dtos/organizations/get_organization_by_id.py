from dataclasses import dataclass


@dataclass
class GetOrganizationByIdRequest:
    organization_id: str
    user_id: str


@dataclass
class OrganizationResponseDTO:
    id: str
    name: str
    slug: str
    is_active: bool
