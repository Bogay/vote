from typing import Protocol, Annotated
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from surrealdb import Surreal
from vote.domain.user import User


class Comment(BaseModel):
    id: str
    user_id: str
    content: str
    created_at: datetime


class CreateCommentInput(BaseModel):
    topic_id: str
    content: str
    user_id: str
    created_at: datetime


class UpdateCommentInput(BaseModel):
    id: str
    content: str


class AddCommentError(Exception):

    def __init__(self, err: dict) -> None:
        self.err = err


class UpdateCommentError(Exception):
    ...


class CommentRepository(Protocol):
    ###
    async def add(self, input: CreateCommentInput):
        ...

    ###
    async def get(self, topic_id: str) -> list[Comment]:
        ...

    async def get_by_id(self, id: str) -> Comment | None:
        ...

    async def update(self, topic_id: str) -> str:
        ...


class CommentRepositoryImpl:

    def __init__(self, db: Surreal) -> None:
        self.db = db

    ###
    async def get(self, topic_id: str) -> list[Comment]:
        result = await self.db.query(
            'SELECT * FROM comment WHERE topic_id=$topic_id',
            {'topic_id': topic_id})
        result = result[0]['result']
        return [Comment.parse_obj(r) for r in result]

    async def get_by_id(self, id: str) -> Comment | None:
        result = await self.db.query('SELECT * FROM comment WHERE id=$id',
                                     {'id': id})
        result = result[0]['result']
        if len(result) == 0:
            return None
        return Comment.parse_obj(result[0])

    ###
    async def add(self, input: CreateCommentInput) -> str:
        input_dict = input.dict()
        input_dict['created_at'] = input_dict['created_at'].isoformat()
        result = await self.db.query('CREATE comment CONTENT $comment;',
                                     {'comment': input_dict})
        if result[0]['status'] != 'OK':
            raise AddCommentError(result[0])
        print(result)
        return result[0]['result'][0]['id']

    ###
    async def update(self, input: UpdateCommentInput):
        result = await self.db.query(
            'UPDATE comment SET content=$content WHERE id=$comment_id', {
                'comment_id': input.id,
                'content': input.content
            })
        if result[0]['status'] != 'OK':
            raise UpdateCommentError(result[0])
        print(result)


class CommentService:

    def __init__(self, repo: CommentRepository):
        self.repo = repo

    async def get(self, topic_id: str) -> list[Comment]:
        return await self.repo.get(topic_id)

    async def post(self, input: CreateCommentInput) -> str:
        return await self.repo.add(input)

    async def patch(self, user: User, input: UpdateCommentInput):
        comment = await self.repo.get_by_id(input.id)
        if comment.user_id == user.id:
            return await self.repo.update(input)
        else:
            raise UpdateCommentError
