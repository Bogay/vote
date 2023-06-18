from fastapi import APIRouter, Depends, status
from . import get_comment_service
from .auth import get_current_user
from datetime import datetime

from vote.domain.comment import CommentService, UpdateCommentInput, CreateCommentInput, Comment
from vote.domain.user import User

from typing import Annotated
from pydantic import BaseModel

router = APIRouter()


@router.get('/')
async def get_comments(
    topic_id: str,
    svc: Annotated[
        CommentService,
        Depends(get_comment_service),
    ],
) -> list[Comment]:
    return await svc.get(topic_id)


class UpdateCommentRequest(BaseModel):
    content: str


class NewCommentRequest(BaseModel):
    topic_id: str
    content: str


@router.post('/', status_code=status.HTTP_204_NO_CONTENT)
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
    input = CreateCommentInput(
        **req.dict(),
        created_at=datetime.now(),
        user_id=user.id,
    )
    await svc.post(input)


@router.patch('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_comment(
    id: str,
    req: UpdateCommentRequest,
    user: Annotated[
        User,
        Depends(get_current_user),
    ],
    svc: Annotated[
        CommentService,
        Depends(get_comment_service),
    ],
):
    input = UpdateCommentInput(**req.dict(), id=id)
    await svc.patch(user, input)
