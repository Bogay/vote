from fastapi import FastAPI
from vote.api import (
    user,
    auth,
    vote,
    topic,
    healthz,
    comment,
)

app = FastAPI()
app.include_router(auth.router, prefix='/auth')
app.include_router(user.router, prefix='/user')
app.include_router(vote.router, prefix='/vote')
app.include_router(topic.router, prefix='/topic')
app.include_router(healthz.router, prefix='/healthz')
app.include_router(comment.router, prefix='/comment')
