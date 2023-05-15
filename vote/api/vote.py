from fastapi import APIRouter, Query, Depends
from typing import Annotated
from pydantic import BaseModel
from vote.domain.vote import VoteService, CreateVoteInput, Vote
from . import get_vote_service

router = APIRouter()


class VoteResponse(BaseModel):

    @classmethod
    def from_vote(cls, vote: Vote):
        return cls()


class CreateVoteRequest(BaseModel):
    topic_id: str
    option_id: str


@router.get('/')
async def list_vote(
    user: Annotated[str, Query],
    svc: Annotated[
        VoteService,
        Depends(get_vote_service),
    ],
):
    '''
    List vote by user. Users can only see self votes.
    '''
    # TODO: check permission
    votes = [
        VoteResponse.from_vote(v) for v in await svc.get_all()
        if v.user.username == user
    ]
    return votes


@router.post('/')
async def create_vote(
    request: CreateVoteRequest,
    svc: Annotated[
        VoteService,
        Depends(get_vote_service),
    ],
):
    '''
    Create a vote. There should be at most one vote for a topic per user.
    '''
    input = CreateVoteInput(
        # TODO: get username
        username='foo',
        topic_id=request.topic_id,
        option_id=request.option_id,
    )
    await svc.add(input)
