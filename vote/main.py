from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from vote.api import (
    user,
    auth,
    vote,
    topic,
    healthz,
    comment,
)
from vote.api.auth import get_current_user
from vote.domain.user import User
from typing import Annotated


def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=['*'],
        allow_credentials=True,
    )
    app.include_router(auth.router, prefix='/auth')
    app.include_router(user.router, prefix='/user')
    app.include_router(vote.router, prefix='/vote')
    app.include_router(topic.router, prefix='/topic')
    app.include_router(healthz.router, prefix='/healthz')
    app.include_router(comment.router, prefix='/comment')

    @app.get('/me')
    async def get_me(user: Annotated[
        User,
        Depends(get_current_user),
    ]):
        return user

    return app
