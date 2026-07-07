from abc import ABC, abstractmethod


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, payload: dict) -> str: ...

    @abstractmethod
    def decode_token(self, token: str) -> dict: ...
