from pydantic import BaseModel, Field
import importlib


class RepositoryLoad(BaseModel):
    repo_method: str = Field(examples=["UsersRepository.get_by_id"])
    count: int = Field(ge=1, default=1, examples=[1, 5, 10])
    latency: float = Field(ge=0, default=1, examples=[0.1, 1, 5])

    @property
    def method(self):
        module = importlib.import_module('repositories')
        repo_class, method = self.repo_method.split(".")
        return getattr(getattr(module, repo_class), method)


class EndpointLoad(BaseModel):
    repos: list[RepositoryLoad]


class LoaderConfig(BaseModel):
    endpoint: str = Field(examples=["users"])
    rps: float = Field(ge=0, examples=[0.1, 1, 5])
    load: EndpointLoad

    @property
    def url(self) -> str:
        return f"http://localhost:8000/{self.endpoint}"

    class Config:
        json_schema_extra = {
            "example": {
                "endpoint": "users",
                "rps": 1,
                "load": {
                    "repos": [
                        {
                            "repo_method": "UsersRepository.get_by_id",
                            "count": 1,
                            "latency": 1
                        }
                    ]
                }
            }
        }


class LoaderConfigs(BaseModel):
    configs: list[LoaderConfig]

    class Config:
        json_schema_extra = {
            "example": {
                "configs": [
                    {
                        "endpoint": "users",
                        "rps": 10,
                        "load": {
                            "repos": [
                                {
                                    "repo_method": "UsersRepository.get_by_id",
                                    "count": 1,
                                    "latency": 1
                                }
                            ]
                        }
                    },
                    {
                        "endpoint": "schedules",
                        "rps": 1,
                        "load": {
                            "repos": [
                                {
                                    "repo_method": "SchedulesRepository.get_all",
                                    "count": 1,
                                    "latency": 10
                                }
                            ]
                        }
                    }
                ]
            }
        }