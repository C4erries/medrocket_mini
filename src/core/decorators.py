import functools
import logging
import time
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar


def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор повторного выполнения функции при ошибке."""

    if max_retries < 1:
        raise ValueError("max_retries must be >= 1")
    if delay < 0:
        raise ValueError("delay must be >= 0")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == max_retries-1:
                        raise
                    time.sleep(delay)
            pass

        return wrapper

    return decorator

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")

def audit_action(
    action_name: str,
    *,
    log_level: int = logging.INFO,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Логирует старт, успешное завершение и ошибки выполнения функции.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                logging.error("FAILED: %s [action=%s], error=%s", func.__name__, action_name, exc)
                raise
            else:
                logger.log(log_level, "SUCCESS: %s [actions=%s]", func.__name__, action_name)
                return result
            finally:
                logger.debug("FINISH: %s lificycle completed", func.__name__)
        return wrapper
    return decorator

def measure_and_protect(
    operation_name: str,
    *,
    max_duration_seconds: float = 2.0,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Безопасность и контроль времени выполнения."""
    if max_duration_seconds <= 0:
        raise ValueError("max_durations_seconds must be grater then 0")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                # Зачем тут логгировать.
                # Разве наш декоратор должен эту функцию выполнять, логгирования ошибок ?
                logger.error(
                    "FAILED: %s [operation=%s], error=%s",
                    func.__name__, operation_name, exc)
                raise
            else:
                return result
            finally:
                duration = time.perf_counter()-start_time
                if duration > max_duration_seconds:
                    logger.warning(f"SLOW OPERATION: {operation_name} took {duration:.4f}s")
        return wrapper
    return decorator
