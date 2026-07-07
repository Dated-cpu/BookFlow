from passlib.context import CryptContext

from src.application.ports.password_hasher import PasswordHasher

_pctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, plain: str) -> str:
        return _pctx.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return _pctx.verify(plain, hashed)
