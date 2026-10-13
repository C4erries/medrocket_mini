import functools
import time
from collections.abc import Callable
from typing import Any


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
