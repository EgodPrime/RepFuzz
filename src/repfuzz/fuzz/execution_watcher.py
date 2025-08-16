import signal
import threading
from typing import Callable


def watchT(timeout_seconds: float, timeout_handler: Callable, error_handler: Callable):
    """
    Decorator that watch the execution of the decorated function.

    Args:
      timeout_seconds (int): The timeout in seconds to be applied to the decorated function.
      timeout_handler (Callable): A function that handles the timeout.
      error_handler (Callable): A function that handles the other errors.
    """

    def wrap(func):
        def to_do(*args, **kwargs):
            def run():
                func(*args, **kwargs)

            t = threading.Thread(target=run)
            try:
                t.start()
                t.join(timeout_seconds)
                if t.is_alive():
                    timeout_handler(
                        TimeoutError(f"Execution takes more than {timeout_seconds:.2f} seconds")
                    )
            except Exception as e:
                error_handler(e)

        return to_do

    return wrap


def watchS(timeout_seconds: float, timeout_handler: Callable, error_handler: Callable):
    """
    Decorator that watch the execution of the decorated function.

    Args:
      timeout_seconds (int): The timeout in seconds to be applied to the decorated function.
      timeout_handler (Callable): A function that handles the timeout.
      error_handler (Callable): A function that handles the other errors.
    """

    def handle_timeout(signum, frame):
        raise TimeoutError(f"Execution takes more than {timeout_seconds:.2f} seconds")

    def wrap(func):
        def to_do(*args, **kwargs):
            signal.signal(signal.SIGALRM, handle_timeout)
            try:
                signal.setitimer(signal.ITIMER_REAL, timeout_seconds)
                func(*args, **kwargs)
                signal.setitimer(signal.ITIMER_REAL, 0)
            except TimeoutError as e:
                signal.setitimer(signal.ITIMER_REAL, 0)
                timeout_handler(e)
            except Exception as e:
                signal.setitimer(signal.ITIMER_REAL, 0)
                error_handler(e)

        return to_do

    return wrap


def watchE(error_handler: Callable):
    def wrap(func):
        def to_do(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as e:
                error_handler(e)

        return to_do

    return wrap


watch = watchE
