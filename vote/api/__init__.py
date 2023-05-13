from typing import Annotated
from surrealdb import Surreal
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from vote.domain.user import UserRepository, UserRepositoryImpl, UserService
from vote.domain.topic import TopicService, TopicRepositoryImpl

oauth2_schema = OAuth2PasswordBearer(tokenUrl='token')


async def get_db():
    db = Surreal('ws://localhost:8080/rpc')
    async with db as db:
        await db.signin({'user': 'root', 'pass': 'root'})
        await db.use('vote', 'vote')
        yield db


async def get_user_repository(db: Annotated[
    Surreal,
    Depends(get_db),
]):
    return UserRepositoryImpl(db)


async def get_user_service(repo: Annotated[
    UserRepository,
    Depends(get_user_repository),
]):
    return UserService(repo)


async def get_topic_service(db: Annotated[
    Surreal,
    Depends(get_db),
]):
    return TopicService(TopicRepositoryImpl(db))
