from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt
from typing import Annotated, Coroutine
from pydantic import BaseModel

from . import oauth2_schema, get_user_service
from vote.domain.user import UserRepository, UserService, create_access_token

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)],
    svc: Annotated[UserRepository, Depends(get_user_service)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, 'foobar', algorithms=['HS256'])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = svc.get_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    svc: Annotated[UserService, Depends(get_user_service)],
):
    user = await svc.authenticate_user(
        form_data.username,
        form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    # TODO: config
    access_token_expires = timedelta(minutes=300)
    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type='bearer',
    )
