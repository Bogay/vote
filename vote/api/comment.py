from fastapi import APIRouter, Depends
from . import get_comment_service
from .auth import get_current_user

from vote.domain.comment import CommentService
from vote.domain.user import User

from typing import Annotated

router = APIRouter()

# CRUD


@router.get('/')
async def get_comments(topic_id: str):
    pass


# @router.get('/{id}')
# async def get_comment(id: str):
#     pass


class NewCommentRequest:
    topic_id: str
    content: str


class NewCommentInput:
    topic_id: str
    content: str


@router.post('/')
async def new_comment(
    req: NewCommentRequest,
    user: Annotated[
        User,
        Depends(get_current_user),
    ],
    svc: Annotated[
        CommentService,
        Depends(get_comment_service),
    ],
):
    input = NewCommentInput(...)
    await svc.add(user, input)


@router.patch('/{id}')
async def update_comment():
    pass

# Client <---> (FastAPI) (Flask) (Django) <---> CommentService <---> CommentRepository <---> (SurrealDB) (MySQL) (PostgreSQL)
