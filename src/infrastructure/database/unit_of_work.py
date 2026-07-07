from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.unit_of_work import UnitOfWork
from src.infrastructure.database.repositories.appointment import SQLAlchemyAppointmentRepository
from src.infrastructure.database.repositories.client import SQLAlchemyClientRepository
from src.infrastructure.database.repositories.employee import SQLAlchemyEmployeeRepository
from src.infrastructure.database.repositories.organization import SQLAlchemyOrganizationRepository
from src.infrastructure.database.repositories.organization_member import (
    SQLAlchemyOrganizationMemberRepository,
)
from src.infrastructure.database.repositories.service import SQLAlchemyServiceRepository
from src.infrastructure.database.repositories.user import SQLAlchemyUserRepository


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.users = SQLAlchemyUserRepository(session)
        self.organizations = SQLAlchemyOrganizationRepository(session)
        self.organization_members = SQLAlchemyOrganizationMemberRepository(session)
        self.employees = SQLAlchemyEmployeeRepository(session)
        self.services = SQLAlchemyServiceRepository(session)
        self.clients = SQLAlchemyClientRepository(session)
        self.appointments = SQLAlchemyAppointmentRepository(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        exc_type = args[0]
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
