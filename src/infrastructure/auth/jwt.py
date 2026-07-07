from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from src.application.ports.token_service import TokenService


class JWTTokenService(TokenService):
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(self, payload: dict) -> str:
        to_encode = payload.copy()
        expire = datetime.now(UTC) + timedelta(minutes=self._access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError:
            raise ValueError("Invalid or expired token")
