from surrealdb import Surreal
from typing import Protocol, Annotated
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from jose import jwt


def verify_password(
    password: str,
    digest: str,
):
    return bcrypt.verify(password, digest)


def get_password_digest(password: str):
    return bcrypt.hash(password)


class User(BaseModel):
    id: str
    username: str
    email: EmailStr
    password_digest: str
    roles: list[str]
    last_login_at: datetime | None
    created_at: datetime
    disabled: bool


class SignupUserInput(BaseModel):
    username: Annotated[str, Field(min_length=1, max_length=16)]
    email: EmailStr
    password: Annotated[
        str,
        Field(description='Hashed user password. '
              'Hash should be done before send it out.'),
    ]


class AddUserInput(BaseModel):
    username: str = Field(min_length=1, max_length=16)
    email: EmailStr
    password_digest: str
    roles: list[str]
    created_at: datetime
    disabled: bool

    @classmethod
    def from_input(cls, input: SignupUserInput):
        return cls(
            username=input.username,
            email=input.email,
            password_digest=get_password_digest(input.email),
            roles=[],
            created_at=datetime.now(),
            disabled=False,
        )


class UserRepository(Protocol):

    async def get_by_username(self, username: str) -> User | None:
        ...

    async def add(self, input: SignupUserInput):
        ...


class UserRepositoryImpl:

    def __init__(self, db: Surreal):
        self.db = db

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.query(
            'SELECT * FROM user WHERE username = $username',
            {'username': username},
        )
        result = result[0]['result']
        if len(result) == 0:
            return None
        return User.parse_obj(result[0])

    async def add(self, input: AddUserInput):
        input_dict = input.dict()
        input_dict['created_at'] = input_dict['created_at'].isoformat()
        await self.db.query('INSERT INTO user $user', {'user': input_dict})


class UserService:

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def authenticate_user(
        self,
        username: str,
        password: str,
    ):
        user = await self.get_by_username(username)
        if user is None:
            return None
        if not verify_password(password, user.password_digest):
            return None
        return user

    async def signup(self, input: SignupUserInput):
        a_input = AddUserInput.from_input(input).dict()
        await self.repo.add(a_input)

    async def get_by_username(self, username: str):
        return await self.repo.get_by_username(username)


def create_access_token(data: dict, expires_after: timedelta | None = None):
    to_encode = data.copy()
    if expires_after is None:
        expires_after = timedelta(minutes=15)
    expires_at = datetime.now() + expires_after
    to_encode.update({'exp': expires_at})
    encoded_jwt = jwt.encode(
        to_encode,
        'foobar',
        algorithm='HS256',
    )
    return encoded_jwt
