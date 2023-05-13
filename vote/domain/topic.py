from typing import Protocol, Annotated
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from surrealdb import Surreal


class TopicStage(str, Enum):
    NOT_STARTED = 'NOT_STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    ENDED = 'ENDED'


class Option(BaseModel):
    id: str
    label: str
    description: str


class CreateOptionInput(BaseModel):
    label: Annotated[str, Field(min_length=1, max_length=64)]
    description: str


class CreateTopicInput(BaseModel):
    description: Annotated[str, Field(default_factory=str)]
    starts_at: datetime
    ends_at: datetime
    options: list[CreateOptionInput]


class UpdateTopicInput(BaseModel):
    description: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    updated_at: datetime
    options: list[Option]
    stage: TopicStage


class Topic(BaseModel):
    id: str
    description: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    updated_at: datetime
    options: list[Option]
    stage: TopicStage

    def update_time_duration(self, starts_at: datetime, ends_at: datetime):
        pass

    def update(self, input: UpdateTopicInput):
        '''
        Update topic inplace.
        '''


class TopicRepository(Protocol):

    async def add(self, input: CreateTopicInput):
        ...

    async def get_by_id(self, id: str) -> Topic | None:
        ...

    async def save(self, topic: Topic):
        ...

    async def get_all(self) -> list[Topic]:
        ...


class TopicRepositoryImpl:

    def __init__(self, db: Surreal) -> None:
        self.db = db


class TopicService:

    def __init__(self, repo: TopicRepository) -> None:
        self.repo = repo

    async def new(self):
        ...

    async def save(self, topic: Topic):
        ...

    async def get_by_id(self, id: str) -> Topic | None:
        ...

    async def get_all(self) -> list[Topic]:
        ...
