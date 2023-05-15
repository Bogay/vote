from typing import Protocol, Annotated
from pydantic import BaseModel, Field
from vote.domain.user import User
from vote.domain.topic import Topic, Option
from surrealdb import Surreal


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

    async def add(self, input: CreateVoteInput):
        ...

    async def get_by_id(self, id: str) -> Vote | None:
        ...

    async def save(self, topic: Vote):
        ...

    async def get_all(self) -> list[Vote]:
        ...


class VoteRepositoryImpl:

    def __init__(self, db: Surreal) -> None:
        self.db = db


class VoteService:

    def __init__(self, repo: VoteRepository) -> None:
        self.repo = repo

    async def get_all(self) -> list[Vote]:
        ...

    async def add(self, input: CreateVoteInput):
        ...
