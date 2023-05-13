from fastapi import APIRouter, Query
from typing import Annotated
from pydantic import BaseModel

router = APIRouter()


class CreateVoteRequest(BaseModel):
    topic_id: str
    option_id: str


@router.get('/')
async def list_vote(user: Annotated[str, Query]):
    '''
    List vote by user. Users can only see self votes.
    '''


@router.post('/')
async def create_vote(input: CreateVoteRequest):
    '''
    Create a vote. There should be at most one vote for a topic per user.
    '''
