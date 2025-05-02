from asyncio import sleep
from random import random

from logs import log_repo_metrics


class BaseRepository:
    @classmethod
    @log_repo_metrics
    async def get_by_id(cls, latency: int) -> None:
        await sleep(latency + random())  # добавляем рандом, чтобы метрики не выглядели неестественно целыми.

    @classmethod
    @log_repo_metrics
    async def get_all(cls, latency: int) -> None:
        await sleep(latency + random())

    @classmethod
    @log_repo_metrics
    async def update(cls, latency: int) -> None:
        await sleep(latency + random())


class UsersRepository(BaseRepository):
    pass

class SchedulesRepository(BaseRepository):
    pass

class ReceptionsRepository(BaseRepository):
    pass
