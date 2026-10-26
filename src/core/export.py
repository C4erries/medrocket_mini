import logging
import time
from collections.abc import Iterable, Iterator
from types import TracebackType
from typing import TypeVar

logger = logging.getLogger(__name__)

class SafeBatchProcessor:
    def __init__(self, batch_name: str) -> None:
        self.batch_name: str = batch_name
        self.start_time: float = 0.0
        self.processed_count: int = 0


    def __enter__(self) -> "SafeBatchProcessor":
        self.start_time = time.perf_counter()
        self.processed_count = 0
        return self

    def track_item(self) -> None:
        self.processed_count += 1

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        duration = time.perf_counter()-self.start_time
        if exc_type is not None:
            logger.error(f"Safe batch processing {self.batch_name} failed with error={exc_val}")
        logger.info(
            f"""
            Batch {self.batch_name} processed {self.processed_count} items in {duration:.4f}s
            """
        )


T = TypeVar("T")
def chunked_iterable[T](source: Iterable[T], chunk_size: int) -> Iterator[list[T]]:
    if chunk_size < 1:
        raise ValueError("size of chunk must be greater then zero")

    chunk = []
    for el in source:
        chunk.append(el)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []

    if chunk:
        yield chunk

