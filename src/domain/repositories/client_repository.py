from abc import ABC

from src.domain.entities.client import Client
from src.domain.repositories.base import AbstractBaseRepository


class ClientRepository(AbstractBaseRepository[Client], ABC):
    pass
