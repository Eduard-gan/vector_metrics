import asyncio
from time import time

import httpx

from schemas import LoaderConfig, EndpointLoad


class LoadGenerator:
    tasks: dict[str, asyncio.Task]
    configs: dict[str, LoaderConfig]

    def __init__(self) -> None:
        self.tasks = {}
        self.configs = {}

    @staticmethod
    async def api_request(url: str, load: EndpointLoad) -> None:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url=url, json=load.model_dump())
        except Exception as e:
            print(f"Load generator error: {repr(e)}")

    async def set_load(self, config: LoaderConfig) -> None:
        """
        При поступлении запроса на нагрузку, мы обязательно актуализируем конфиг нагрузки для эндпоинта.
        В случае наличия задачи по этому эндпоинту, отменяем пересоздаем её в любом случае.
        """

        self.configs[config.endpoint] = config
        if config.endpoint in self.tasks:
            self.tasks[config.endpoint].cancel()
        self.tasks[config.endpoint] = asyncio.create_task(self.load(config))
        print(f"SET LOAD FOR {config.url} TO {config.rps} RPS WITH PROFILE {config.load.model_dump()}")

    async def load(self, config: LoaderConfig) -> None:
        if config.rps <= 0:
            return

        targeted_time_between_requests = 1 / config.rps

        last_request_time = time()
        while True:
            time_between_requests = time() - last_request_time
            if time_between_requests >= targeted_time_between_requests:
                await asyncio.create_task(self.api_request(url=config.url, load=config.load))
                last_request_time = time()
