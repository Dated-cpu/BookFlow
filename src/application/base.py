from abc import ABC, abstractmethod


class BaseUseCase[Request, Response](ABC):
    @abstractmethod
    async def execute(self, request: Request) -> Response: ...
