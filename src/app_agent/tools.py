from collections.abc import Callable
from time import sleep
from typing import TypeVar

T = TypeVar("T")


def retry_call(fn: Callable[[], T], attempts: int = 3, delay_seconds: float = 1.0) -> T:
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as error:
            last_error = error
            if attempt < attempts:
                sleep(delay_seconds)

    raise RuntimeError(f"Operation failed after {attempts} attempts") from last_error
