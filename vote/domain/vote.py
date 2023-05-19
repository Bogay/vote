from typing import Protocol, Annotated
from pydantic import BaseModel, Field
from vote.domain.user import User
from vote.domain.topic import Topic, Option
from surrealdb import Surreal


class Vote(BaseModel):
    id: str
    username: str
    topic_id: str
    option_id: str


class CreateVoteInput(BaseModel):
    topic_id: str
    option_id: str


class DuplicatedVoteError(Exception):
    # TODO: add param
    pass


class AddVoteError(Exception):

    def __init__(self, err: dict) -> None:
        self.err = err


class InitVoteError(Exception):

    def __init__(self, err: list[dict]) -> None:
        self.err = err


class VoteRepository(Protocol):

    async def add(self, username: str, input: CreateVoteInput):
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

    async def init_db(self):
        results = await self.db.query('''
        DEFINE TABLE vote;
        DEFINE FIELD username ON TABLE vote TYPE string
            ASSERT $value != None;
        DEFINE FIELD topic_id ON TABLE vote TYPE string
            ASSERT $value != None;
        DEFINE FIELD option_id ON TABLE vote TYPE string
            ASSERT $value != None;

        DEFINE INDEX topic_id_index ON TABLE vote COLUMNS username, topic_id UNIQUE;
        ''')
        if not all(r['status'] == 'OK' for r in results):
            raise InitVoteError(results)

    async def add(self, username: str, input: CreateVoteInput):
        input_dict = input.dict()
        input_dict['username'] = username
        result = await self.db.query(
            'CREATE vote CONTENT $vote;',
            {'vote': input_dict},
        )
        if result[0]['status'] != 'OK':
            raise AddVoteError(result[0])

    async def get_by_id(self, id: str) -> Vote | None:
        ...

    async def save(self, topic: Vote):
        ...

    async def get_all(self) -> list[Vote]:
        return []


class VoteService:

    def __init__(self, repo: VoteRepository) -> None:
        self.repo = repo

    async def get_all(self) -> list[Vote]:
        return await self.repo.get_all()

    async def add(self, username: str, input: CreateVoteInput):
        votes = await self.repo.get_all()
        if any(v.username == username and v.topic_id == input.topic_id
               for v in votes):
            raise DuplicatedVoteError()
        await self.repo.add(username, input)
