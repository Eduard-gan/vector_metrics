import logging
import sys
from collections import OrderedDict
from enum import Enum
from functools import wraps
from time import time

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


def get_caller_name(fn, args) -> str:
    """
    Возвращает имя функции или метода, который вызвал декорируемую функцию в dot-нотации.
    """

    func_or_method = fn.__name__
    if args and hasattr(args[0], '__class__') and not isinstance(args[0], type):
        calling_class = args[0].__class__.__name__
    elif args and isinstance(args[0], type):
        calling_class = args[0].__name__
    else:
        calling_class = None

    return f"{calling_class}.{func_or_method}" if calling_class else func_or_method


def log_repo_metrics(fn):
    """
    Декоратор может использоваться для методов, класс-методов и обычных функций, только в их асинхронном варианте.
    Статик-методы не поддерживаются и будут выглядеть, как обычные отдельно стоящие функции.
    """

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        start_time = time()
        result = await fn(*args, **kwargs)
        elapsed = round(time() - start_time, 3)

        structlog.get_logger().info(**Field.MetricName(get_caller_name(fn, args)), **Field.Elapsed(elapsed))
        return result
    return wrapper
