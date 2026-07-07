from fastapi import APIRouter, Depends, status

from src.application.dtos.organizations.create_organization import (
    CreateOrganizationRequest as CreateOrgAppRequest,
)
from src.application.dtos.organizations.get_my_organizations import (
    GetMyOrganizationsRequest,
)
from src.application.dtos.organizations.get_organization_by_id import (
    GetOrganizationByIdRequest,
)
from src.application.use_cases.organizations.create_organization import CreateOrganization
from src.application.use_cases.organizations.get_my_organizations import GetMyOrganizations
from src.application.use_cases.organizations.get_organization_by_id import GetOrganizationById
from src.domain.entities.user import User
from src.presentation.api.v1.dependencies import (
    get_create_org_use_case,
    get_current_user,
    get_my_organizations_use_case,
    get_organization_by_id_use_case,
)
from src.presentation.api.v1.schemas.organizations import (
    OrganizationCreateRequest,
    OrganizationCreateResponse,
    OrganizationResponse,
    OrganizationWithRoleResponse,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "",
    response_model=OrganizationCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    body: OrganizationCreateRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateOrganization = Depends(get_create_org_use_case),
) -> OrganizationCreateResponse:
    app_request = CreateOrgAppRequest(name=body.name, owner_user_id=str(current_user.id))
    result = await use_case.execute(app_request)
    return OrganizationCreateResponse(
        id=result.id,
        name=result.name,
        slug=result.slug,
    )


@router.get(
    "",
    response_model=list[OrganizationWithRoleResponse],
    status_code=status.HTTP_200_OK,
)
async def list_my_organizations(
    current_user: User = Depends(get_current_user),
    use_case: GetMyOrganizations = Depends(get_my_organizations_use_case),
) -> list[OrganizationWithRoleResponse]:
    app_request = GetMyOrganizationsRequest(user_id=str(current_user.id))
    result = await use_case.execute(app_request)
    return [
        OrganizationWithRoleResponse(
            id=item.id,
            name=item.name,
            slug=item.slug,
            role=item.role,
        )
        for item in result
    ]


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_organization(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    use_case: GetOrganizationById = Depends(get_organization_by_id_use_case),
) -> OrganizationResponse:
    app_request = GetOrganizationByIdRequest(
        organization_id=organization_id,
        user_id=str(current_user.id),
    )
    result = await use_case.execute(app_request)
    return OrganizationResponse(
        id=result.id,
        name=result.name,
        slug=result.slug,
        is_active=result.is_active,
    )
