from fastapi import APIRouter, Depends
from vote.domain.user import SignupUserInput, UserService
from pydantic import BaseModel
from typing import Annotated
from . import get_user_service

router = APIRouter()


class SignupResponse(BaseModel):
    pass


@router.post('/signup')
async def signup(
    input: SignupUserInput,
    svc: Annotated[
        UserService,
        Depends(get_user_service),
    ],
):
    # TODO: unit of work (lock?)
    await svc.signup(input)
    return SignupResponse()


@router.get('/{username}')
async def get_by_username(
    username: str,
    svc: Annotated[
        UserService,
        Depends(get_user_service),
    ],
):
    user = await svc.get_by_username(username)
    # FIXME: directly return user model to frontend is not a good idea
    return user
