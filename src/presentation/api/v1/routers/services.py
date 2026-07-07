from fastapi import APIRouter, Depends, status

from src.application.dtos.services.create_service import (
    CreateServiceRequest as CreateServiceAppRequest,
)
from src.application.dtos.services.delete_service import DeleteServiceRequest
from src.application.dtos.services.get_service import GetServiceRequest
from src.application.dtos.services.list_services import ListServicesRequest
from src.application.dtos.services.update_service import (
    UpdateServiceRequest as UpdateServiceAppRequest,
)
from src.application.use_cases.services.create_service import CreateService
from src.application.use_cases.services.delete_service import DeleteService
from src.application.use_cases.services.get_service import GetServiceById
from src.application.use_cases.services.list_services import ListServices
from src.application.use_cases.services.update_service import UpdateService
from src.domain.entities.user import User
from src.presentation.api.v1.dependencies import (
    get_create_service_use_case,
    get_current_user,
    get_delete_service_use_case,
    get_list_services_use_case,
    get_service_by_id_use_case,
    get_update_service_use_case,
)
from src.presentation.api.v1.schemas.services import (
    ServiceCreateRequest,
    ServiceResponse,
    ServiceUpdateRequest,
)

router = APIRouter(prefix="/services", tags=["services"])


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(
    body: ServiceCreateRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateService = Depends(get_create_service_use_case),
) -> ServiceResponse:
    app_request = CreateServiceAppRequest(
        organization_id=body.organization_id,
        owner_user_id=str(current_user.id),
        name=body.name,
        price=body.price,
        duration_minutes=body.duration_minutes,
        description=body.description,
    )
    result = await use_case.execute(app_request)
    return ServiceResponse(
        id=result.id,
        organization_id=result.organization_id,
        name=result.name,
        price=result.price,
        duration_minutes=result.duration_minutes,
        description=result.description,
        is_active=result.is_active,
    )


@router.get(
    "",
    response_model=list[ServiceResponse],
    status_code=status.HTTP_200_OK,
)
async def list_services(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    use_case: ListServices = Depends(get_list_services_use_case),
) -> list[ServiceResponse]:
    app_request = ListServicesRequest(
        organization_id=organization_id,
        user_id=str(current_user.id),
    )
    result = await use_case.execute(app_request)
    return [
        ServiceResponse(
            id=s.id,
            organization_id=s.organization_id,
            name=s.name,
            price=s.price,
            duration_minutes=s.duration_minutes,
            description=s.description,
            is_active=s.is_active,
        )
        for s in result
    ]


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
)
async def get_service(
    service_id: str,
    current_user: User = Depends(get_current_user),
    use_case: GetServiceById = Depends(get_service_by_id_use_case),
) -> ServiceResponse:
    app_request = GetServiceRequest(
        service_id=service_id,
        user_id=str(current_user.id),
    )
    result = await use_case.execute(app_request)
    return ServiceResponse(
        id=result.id,
        organization_id=result.organization_id,
        name=result.name,
        price=result.price,
        duration_minutes=result.duration_minutes,
        description=result.description,
        is_active=result.is_active,
    )


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
)
async def update_service(
    service_id: str,
    body: ServiceUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_case: UpdateService = Depends(get_update_service_use_case),
) -> ServiceResponse:
    app_request = UpdateServiceAppRequest(
        service_id=service_id,
        user_id=str(current_user.id),
        name=body.name,
        price=body.price,
        duration_minutes=body.duration_minutes,
        description=body.description,
        is_active=body.is_active,
    )
    result = await use_case.execute(app_request)
    return ServiceResponse(
        id=result.id,
        organization_id=result.organization_id,
        name=result.name,
        price=result.price,
        duration_minutes=result.duration_minutes,
        description=result.description,
        is_active=result.is_active,
    )


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service(
    service_id: str,
    current_user: User = Depends(get_current_user),
    use_case: DeleteService = Depends(get_delete_service_use_case),
) -> None:
    app_request = DeleteServiceRequest(
        service_id=service_id,
        user_id=str(current_user.id),
    )
    await use_case.execute(app_request)
