from typing import Protocol, Annotated
from pydantic import BaseModel, Field
from vote.domain.user import User
from vote.domain.topic import Topic, Option


class Vote(BaseModel):
    id: str
    user: User
    topic: Topic
    option: Option


class CreateVoteInput(BaseModel):
    username: str
    topic_id: str
    option_id: str


class VoteRepository(Protocol):
    ...


class VoteService:
    ...
