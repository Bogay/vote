from fastapi import APIRouter, Query, Depends
from typing import Annotated
from pydantic import BaseModel
from vote.domain.user import User
from vote.domain.vote import VoteService, CreateVoteInput, Vote
from . import get_vote_service
from .auth import get_current_user

router = APIRouter()


class VoteResponse(BaseModel):
    username: str
    topic_id: str
    option_id: str

    @classmethod
    def from_vote(cls, vote: Vote):
        return cls.from_orm(vote)

    class Config:
        orm_mode = True


@router.get('/')
async def list_vote(
    user: Annotated[str | None, Query],
    svc: Annotated[
        VoteService,
        Depends(get_vote_service),
    ],
    current_user: Annotated[User, Depends(get_current_user)],
):
    '''
    List vote by user. Users can only see self votes.
    '''
    if user is None:
        user = current_user.username
    # TODO: check permission
    votes = [
        VoteResponse.from_vote(v) for v in await svc.get_all()
        if v.username == user
    ]
    return votes


@router.post('/')
async def create_vote(
    input: CreateVoteInput,
    svc: Annotated[
        VoteService,
        Depends(get_vote_service),
    ],
    user: Annotated[User, Depends(get_current_user)],
):
    '''
    Create a vote. There should be at most one vote for a topic per user.
    '''
    await svc.add(user.username, input)
