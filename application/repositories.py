from asyncio import sleep
from random import uniform

from logs import log_repo_metrics


def jitter(latency: float, min_percent: int = 0, max_percent: int = 5) -> float:
    jitter_percent = uniform(min_percent, max_percent)
    return latency * jitter_percent / 100


async def workload(latency: float, add_jitter: bool = True) -> None:
    amount = latency
    if add_jitter:
        amount += jitter(latency)
    await sleep(amount)


class BaseRepository:
    @classmethod
    @log_repo_metrics
    async def get_by_id(cls, latency: int) -> None:
        await workload(latency)

    @classmethod
    @log_repo_metrics
    async def get_all(cls, latency: int) -> None:
        await workload(latency)

    @classmethod
    @log_repo_metrics
    async def update(cls, latency: int) -> None:
        await workload(latency)


class UsersRepository(BaseRepository):
    pass

class SchedulesRepository(BaseRepository):
    pass

class ReceptionsRepository(BaseRepository):
    pass
