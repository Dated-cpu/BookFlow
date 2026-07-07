from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.appointment import AppointmentModel
    from src.infrastructure.database.models.client import ClientModel
    from src.infrastructure.database.models.employee import EmployeeModel
    from src.infrastructure.database.models.organization_member import OrganizationMemberModel
    from src.infrastructure.database.models.service import ServiceModel


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    members: Mapped[list[OrganizationMemberModel]] = relationship(back_populates="organization")
    employees: Mapped[list[EmployeeModel]] = relationship(back_populates="organization")
    services: Mapped[list[ServiceModel]] = relationship(back_populates="organization")
    clients: Mapped[list[ClientModel]] = relationship(back_populates="organization")
    appointments: Mapped[list[AppointmentModel]] = relationship(back_populates="organization")
