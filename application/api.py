import asyncio
import uvicorn
import logging
from fastapi import FastAPI

from load_generator import LoadGenerator
from schemas import EndpointLoad, LoaderConfigs


app = FastAPI()
app.load_generator = LoadGenerator()

# Отключение логов httpx
for logger_nbame in ("httpcore", "httpx"):
    logger = logging.getLogger(logger_nbame)
    logger.addHandler(logging.NullHandler())
    logger.propagate = False


async def process_load(load: EndpointLoad) -> None:
    for repo in load.repos:
        for _ in range(repo.count):
            asyncio.create_task(repo.method(repo.latency))


@app.post("/users")
async def users_endpoint(load: EndpointLoad) -> None:
    await process_load(load)


@app.post("/schedules")
async def schedules_endpoint(load: EndpointLoad) -> None:
    await process_load(load)


@app.post("/receptions")
async def receptions_endpoint(load: EndpointLoad) -> None:
    await process_load(load)


@app.post("/set_load")
async def set_load(config: LoaderConfigs) -> None:
    for config in config.configs:
        await app.load_generator.set_load(config)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
