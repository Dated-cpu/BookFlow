from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import AuthenticationError
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.token_service import TokenService
from src.application.use_cases.appointments.cancel_appointment import CancelAppointment
from src.application.use_cases.appointments.create_appointment import CreateAppointment
from src.application.use_cases.appointments.get_appointment import GetAppointmentById
from src.application.use_cases.appointments.list_appointments import ListAppointments
from src.application.use_cases.appointments.update_appointment import UpdateAppointment
from src.application.use_cases.auth.login_user import LoginUser
from src.application.use_cases.auth.register_user import RegisterUser
from src.application.use_cases.employees.create_employee import CreateEmployee
from src.application.use_cases.employees.delete_employee import DeleteEmployee
from src.application.use_cases.employees.get_employee import GetEmployeeById
from src.application.use_cases.employees.list_employees import ListEmployees
from src.application.use_cases.employees.update_employee import UpdateEmployee
from src.application.use_cases.organizations.create_organization import CreateOrganization
from src.application.use_cases.organizations.get_my_organizations import GetMyOrganizations
from src.application.use_cases.organizations.get_organization_by_id import GetOrganizationById
from src.application.use_cases.services.create_service import CreateService
from src.application.use_cases.services.delete_service import DeleteService
from src.application.use_cases.services.get_service import GetServiceById
from src.application.use_cases.services.list_services import ListServices
from src.application.use_cases.services.update_service import UpdateService
from src.domain.entities.user import User as UserEntity
from src.infrastructure.auth.jwt import JWTTokenService
from src.infrastructure.auth.password import BcryptPasswordHasher
from src.infrastructure.config.settings import Settings
from src.infrastructure.database.engine import get_session
from src.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

_bearer = HTTPBearer(auto_error=False)


def get_settings() -> Settings:
    return Settings()


async def get_uow(
    session: AsyncSession = Depends(get_session),
) -> SQLAlchemyUnitOfWork:
    return SQLAlchemyUnitOfWork(session)


def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


async def get_token_service(
    settings: Settings = Depends(get_settings),
) -> TokenService:
    return JWTTokenService(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
    )


async def get_register_user_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> RegisterUser:
    return RegisterUser(
        user_repo=uow.users,
        password_hasher=password_hasher,
        uow=uow,
    )


async def get_login_user_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> LoginUser:
    return LoginUser(
        user_repo=uow.users,
        password_hasher=password_hasher,
        token_service=token_service,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
) -> UserEntity:
    if credentials is None:
        raise AuthenticationError("Not authenticated")
    try:
        payload = token_service.decode_token(credentials.credentials)
    except ValueError:
        raise AuthenticationError("Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token")
    user = await uow.users.get_by_id(UUID(user_id))
    if not user:
        raise AuthenticationError("User not found")
    return user


async def get_create_org_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> CreateOrganization:
    return CreateOrganization(
        org_repo=uow.organizations,
        org_member_repo=uow.organization_members,
        uow=uow,
    )


async def get_my_organizations_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> GetMyOrganizations:
    return GetMyOrganizations(
        org_repo=uow.organizations,
        org_member_repo=uow.organization_members,
    )


async def get_organization_by_id_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> GetOrganizationById:
    return GetOrganizationById(
        org_repo=uow.organizations,
        org_member_repo=uow.organization_members,
    )


async def get_create_employee_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> CreateEmployee:
    return CreateEmployee(
        employee_repo=uow.employees,
        org_member_repo=uow.organization_members,
        uow=uow,
    )


async def get_list_employees_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> ListEmployees:
    return ListEmployees(
        employee_repo=uow.employees,
        org_member_repo=uow.organization_members,
    )


async def get_employee_by_id_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> GetEmployeeById:
    return GetEmployeeById(
        employee_repo=uow.employees,
        org_member_repo=uow.organization_members,
    )


async def get_update_employee_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> UpdateEmployee:
    return UpdateEmployee(
        employee_repo=uow.employees,
        org_member_repo=uow.organization_members,
        uow=uow,
    )


async def get_delete_employee_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> DeleteEmployee:
    return DeleteEmployee(
        employee_repo=uow.employees,
        org_member_repo=uow.organization_members,
        uow=uow,
    )


async def get_create_service_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> CreateService:
    return CreateService(
        service_repo=uow.services,
        org_member_repo=uow.organization_members,
        uow=uow,
    )


async def get_list_services_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> ListServices:
    return ListServices(
        service_repo=uow.services,
        org_member_repo=uow.organization_members,
    )


async def get_service_by_id_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> GetServiceById:
    return GetServiceById(
        service_repo=uow.services,
        org_member_repo=uow.organization_members,
    )


async def get_update_service_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> UpdateService:
    return UpdateService(
        service_repo=uow.services,
        org_member_repo=uow.organization_members,
        uow=uow,
    )


async def get_delete_service_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> DeleteService:
    return DeleteService(
        service_repo=uow.services,
        org_member_repo=uow.organization_members,
        uow=uow,
    )


async def get_create_appointment_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> CreateAppointment:
    return CreateAppointment(
        appointment_repo=uow.appointments,
        employee_repo=uow.employees,
        client_repo=uow.clients,
        service_repo=uow.services,
        org_member_repo=uow.organization_members,
        uow=uow,
    )


async def get_list_appointments_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> ListAppointments:
    return ListAppointments(
        appointment_repo=uow.appointments,
        org_member_repo=uow.organization_members,
    )


async def get_appointment_by_id_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> GetAppointmentById:
    return GetAppointmentById(
        appointment_repo=uow.appointments,
        org_member_repo=uow.organization_members,
    )


async def get_update_appointment_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> UpdateAppointment:
    return UpdateAppointment(
        appointment_repo=uow.appointments,
        org_member_repo=uow.organization_members,
        uow=uow,
    )


async def get_cancel_appointment_use_case(
    uow: SQLAlchemyUnitOfWork = Depends(get_uow),
) -> CancelAppointment:
    return CancelAppointment(
        appointment_repo=uow.appointments,
        org_member_repo=uow.organization_members,
        uow=uow,
    )
