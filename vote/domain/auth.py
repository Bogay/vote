from datetime import timedelta, datetime
from typing import Protocol, Any
from pydantic import BaseModel
from jose import jwt


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str


class AuthConfigRepository(Protocol):

    def get(self) -> AuthConfig:
        ...


class AuthConfigRepositoryImpl:

    def __init__(self, config_str: str) -> None:
        '''
        Load from json string
        '''
        self.config = AuthConfig.parse_raw(config_str)

    def get(self) -> AuthConfig:
        return self.config


# TODO: maybe an application service?
class AuthService:

    def __init__(self, repo: AuthConfigRepository) -> None:
        self.repo = repo
        self.config = self.repo.get()

    def parse(self, token: str) -> dict[str, Any]:
        payload = jwt.decode(
            token,
            self.config.secret_key,
            algorithms=[self.config.algorithm],
        )
        return payload

    def sign(
        self,
        data: dict[str, Any],
        expires_after: timedelta | None = None,
    ) -> str:
        if expires_after is None:
            expires_after = timedelta(minutes=15)

        expires_at = datetime.now() + expires_after
        to_encode = data.copy() | {'exp': expires_at}
        encoded_jwt = jwt.encode(
            to_encode,
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )

        return encoded_jwt
