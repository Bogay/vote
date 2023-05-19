from surrealdb import Surreal
from typing import Protocol, Annotated
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from passlib.hash import bcrypt


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
              'Hash should be done before send it out. '
              'We don\'t check it server-side.'),
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
            password_digest=get_password_digest(input.password),
            roles=[],
            created_at=datetime.now(),
            disabled=False,
        )


class AddUserError(Exception):

    def __init__(self, err: dict) -> None:
        self.err = err


class InitUserError(Exception):

    def __init__(self, err: list[dict]) -> None:
        self.err = err


class UserRepository(Protocol):

    async def get_by_username(self, username: str) -> User | None:
        ...

    async def add(self, input: AddUserInput):
        ...


class UserRepositoryImpl:

    def __init__(self, db: Surreal):
        self.db = db

    async def init_db(self):
        results = await self.db.query('''
        DEFINE TABLE user;
        DEFINE FIELD username ON TABLE user TYPE string
            ASSERT $value != None;
        DEFINE FIELD email ON TABLE user TYPE string
            ASSERT $value != None
            AND is::email($value);
        DEFINE FIELD password_digest ON TABLE user TYPE string
            ASSERT $value != None;
        DEFINE FIELD roles ON TABLE user TYPE array
            ASSERT $value != None;
        DEFINE FIELD roles.* ON TABLE user TYPE string;
        DEFINE FIELD last_login_at ON TABLE user TYPE datetime;
        DEFINE FIELD created_at ON TABLE user TYPE datetime
            ASSERT $value != None;
        DEFINE FIELD disabled ON TABLE user TYPE bool
            ASSERT $value != None;
        
        DEFINE INDEX email_index ON TABLE user COLUMNS email UNIQUE;
        DEFINE INDEX username_index ON TABLE user COLUMNS username UNIQUE;
        ''')
        if not all(r['status'] == 'OK' for r in results):
            raise InitUserError(results)

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
        result = await self.db.query(
            'CREATE user CONTENT $user;',
            {'user': input_dict},
        )
        if result[0]['status'] != 'OK':
            raise AddUserError(result[0])


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
        a_input = AddUserInput.from_input(input)
        await self.repo.add(a_input)

    async def get_by_username(self, username: str):
        return await self.repo.get_by_username(username)
