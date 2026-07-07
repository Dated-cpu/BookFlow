from pydantic import BaseModel


class OrganizationCreateRequest(BaseModel):
    name: str


class OrganizationCreateResponse(BaseModel):
    id: str
    name: str
    slug: str


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    is_active: bool


class OrganizationWithRoleResponse(BaseModel):
    id: str
    name: str
    slug: str
    role: str
