from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError
from typing import Annotated
from pydantic import BaseModel

from . import oauth2_schema, get_user_service, get_auth_service
from vote.domain.user import UserService
from vote.domain.auth import AuthService

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
    user_svc: Annotated[UserService, Depends(get_user_service)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = auth_svc.parse(token)
        username = payload.get('sub')
        if username is None or not isinstance(username, str):
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await user_svc.get_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    user_svc: Annotated[UserService, Depends(get_user_service)],
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):
    user = await user_svc.authenticate_user(
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
    access_token = auth_svc.sign(
        data={'sub': user.username},
        expires_after=access_token_expires,
    )
    return Token(
        access_token=access_token,
        token_type='bearer',
    )
