import logging
import sys
from collections import OrderedDict
from random import randint, random, choice
import structlog
from time import sleep, time
from enum import Enum


class Field(Enum):
    """Список полей согласованных для единого формата логов между сервисами."""

    # Могут быть автоматически сгенерированны без явной передачи
    timestamp = "timestamp"  # ISO-8601
    LevelName = "LevelName"  # DEBUG, INFO... устанавливается на основе названия метода .debug
    Environment = "Environment"
    Facility = "Facility"  # Название сервиса
    ActionName = "ActionName"  # Имя функции, где происходит лог.
    TraceId = "TraceId"
    SpanId = "SpanId"

    # Для запросов:
    Elapsed = "Elapsed"
    Headers = "Headers"
    RequestData = "RequestData"
    RequestPath = "RequestPath"
    Url = "Url"
    ResponseData = "ResponseData"

    # Ошибки:
    ExceptionMessage = "ExceptionMessage"
    StackTrace = "StackTrace"

    # Метрики
    MetricName = "MetricName"  # Тэг для метрик, по нему будет посмтроен базовый наборк, количество, среднее и сумарное время исполнения.

    def __call__(self, value) -> dict:
        return {self.value: value}


def ordering_processor(_logger, _name, event_dict) -> dict:
    """Ordering processor for structlog."""

    ordered = OrderedDict(timestamp=None, level=None, event=None)
    for key, value in event_dict.items():
        ordered[key] = value
    return ordered


# Base python logging setup
logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.DEBUG)


# Structlog setup
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S", utc=True),
        structlog.stdlib.add_log_level,
        ordering_processor,
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(sort_keys=False, ensure_ascii=False),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,  # noqa
    cache_logger_on_first_use=True,
)


logger = structlog.get_logger()

def log_metrics(metric_name):
    def inner(func):
        def wrapper(*args, **kwargs):
            start_time = time()
            result = func(*args, **kwargs)
            elapsed = round(time() - start_time, 3)

            logger.info(
                **Field.MetricName(metric_name),
                **Field.Elapsed(elapsed)
            )
            return result
        return wrapper
    return inner


class UserRepository:

    @staticmethod
    def _random_sleep():
        seconds = randint(0, 5) + random()
        sleep(seconds)

    @classmethod
    @log_metrics("UserRepository.get_by_id")
    def get_by_id(cls):
        cls._random_sleep()

    @classmethod
    @log_metrics("UserRepository.get_all")
    def get_all(cls):
        cls._random_sleep()


while True:
    method_names = [x for x in dir(UserRepository) if not x.startswith('_')]
    random_method_name = choice(method_names)
    random_repo_method = getattr(UserRepository, random_method_name)
    random_repo_method()
