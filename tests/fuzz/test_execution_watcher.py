from repfuzz.fuzz.execution_watcher import watch
import time


def handle_timeout(e: Exception):
    raise e


def handle_error(e: Exception):
    raise e


def test_watch_timeout1():
    @watch(1, handle_timeout, handle_error)
    def func_1():
        time.sleep(20)

    try:
        func_1()
    except Exception as e:
        print(e)
        assert isinstance(e, TimeoutError)


def test_watch_timeout2():
    @watch(1, handle_timeout, handle_error)
    def func_2():
        return 2**1000000000

    try:
        t0 = time.time()
        func_2()
        dt = time.time() - t0
        assert dt > 1
        assert dt < 2
    except Exception as e:
        assert isinstance(e, TimeoutError)
