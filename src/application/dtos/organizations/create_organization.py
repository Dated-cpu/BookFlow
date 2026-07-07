from dataclasses import dataclass


@dataclass
class CreateOrganizationRequest:
    name: str
    owner_user_id: str


@dataclass
class CreateOrganizationResponse:
    id: str
    name: str
    slug: str
    membership_id: str
