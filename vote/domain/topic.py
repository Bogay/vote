from typing import Protocol, Annotated
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from surrealdb import Surreal
import secrets


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


class InitTopicError(Exception):

    def __init__(self, err: list[dict]) -> None:
        self.err = err


class AddTopicError(Exception):

    def __init__(self, err: dict) -> None:
        self.err = err


class UpdateTopicError(Exception):
    ...


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

    def refresh(self):
        now = datetime.now(timezone.utc)
        if now < self.starts_at:
            self.stage = TopicStage.NOT_STARTED
        elif self.starts_at <= now <= self.ends_at:
            self.stage = TopicStage.IN_PROGRESS
        else:
            self.stage = TopicStage.ENDED


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

    async def init_db(self):
        results = await self.db.query('''
        DEFINE TABLE topic;
        DEFINE FIELD description ON TABLE topic TYPE string
            ASSERT $value != None;
        DEFINE FIELD starts_at ON TABLE topic TYPE datetime
            ASSERT $value != None;
        DEFINE FIELD ends_at ON TABLE topic TYPE datetime
            ASSERT $value != None;
        DEFINE FIELD created_at ON TABLE topic TYPE datetime
            ASSERT $value != None;
        DEFINE FIELD updated_at ON TABLE topic TYPE datetime
            ASSERT $value != None;
        DEFINE FIELD options ON TABLE topic TYPE array
            ASSERT $value != None;
        DEFINE FIELD stage ON TABLE topic TYPE string
            ASSERT $value inside ["NOT_STARTED", "IN_PROGRESS", "ENDED"];
        ''')

        if not all(r['status'] == 'OK' for r in results):
            raise InitTopicError(results)

    # TODO: relate user and topic
    async def add(self, input: CreateTopicInput) -> str:
        input_dict = input.dict()
        for opt in input_dict['options']:
            opt['id'] = secrets.token_urlsafe()
        input_dict['starts_at'] = input_dict['starts_at'].isoformat()
        input_dict['ends_at'] = input_dict['ends_at'].isoformat()
        input_dict['created_at'] = datetime.now().isoformat()
        input_dict['updated_at'] = datetime.now().isoformat()
        input_dict['stage'] = TopicStage.NOT_STARTED
        result = await self.db.query(
            'CREATE topic CONTENT $topic;',
            {'topic': input_dict},
        )
        if result[0]['status'] != 'OK':
            raise AddTopicError(result[0])
        print(result)
        return result[0]['result'][0]['id']

    async def get_by_id(self, id: str) -> Topic | None:
        result = await self.db.query(
            'SELECT * FROM topic WHERE id = $id',
            {'id': id},
        )
        result = result[0]['result']
        if len(result) == 0:
            return None
        return Topic.parse_obj(result[0])

    async def save(self, topic: Topic):
        topic_dict = topic.dict()
        topic_dict['starts_at'] = topic_dict['starts_at'].isoformat()
        topic_dict['ends_at'] = topic_dict['ends_at'].isoformat()
        topic_dict['created_at'] = topic_dict['created_at'].isoformat()
        topic_dict['updated_at'] = topic_dict['updated_at'].isoformat()
        result = await self.db.query(
            'UPDATE topic CONTENT $content WHERE id=$id;',
            {
                'content': topic_dict,
                'id': topic.id,
            },
        )
        if result[0]['status'] != 'OK':
            raise UpdateTopicError(result[0])

    async def get_all(self) -> list[Topic]:
        result = await self.db.query('SELECT * FROM topic ORDER BY created_at DESC')
        result = result[0]['result']
        return [Topic.parse_obj(r) for r in result]


class TopicService:

    def __init__(self, repo: TopicRepository):
        self.repo = repo

    async def new(self, input: CreateTopicInput) -> str:
        return await self.repo.add(input)

    async def save(self, topic: Topic):
        await self.repo.save(topic)

    async def get_by_id(self, id: str) -> Topic | None:
        return await self.repo.get_by_id(id)

    async def get_all(self) -> list[Topic]:
        return await self.repo.get_all()
