import inspect
import logging
import sys
from collections import OrderedDict
from enum import Enum
from time import time
from typing import Optional

import structlog


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


def get_class_and_method_name(func) -> str:
    method_name = func.__name__
    class_name = None

    if inspect.getfullargspec(func).args and inspect.getfullargspec(func).args[0] in ['self', 'cls']:
        class_name = func.__qualname__.split('.')[0]

    if class_name:
        return f"{class_name}.{method_name}"
    else:
        return method_name


def log_repo_metrics(func):
    async def wrapper(*args, **kwargs):
        metric_name = get_class_and_method_name(func)

        start_time = time()
        result = await func(*args, **kwargs)
        elapsed = round(time() - start_time, 3)

        structlog.get_logger().info(
            **Field.MetricName(metric_name),
            **Field.Elapsed(elapsed)
        )
        return result
    return wrapper
