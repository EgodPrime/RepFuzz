import threading
import time


def func1():
    time.sleep(20)


def func2():
    return 2**1000000000


th = threading.Thread(target=func1)
t0 = time.time()
th.start()
th.join(1)
dt = time.time() - t0
print(f"dt of func1 is {dt}")
assert dt > 1
assert dt < 2

th = threading.Thread(target=func2)
t0 = time.time()
th.start()
th.join(1)
dt = time.time() - t0
print(f"dt of func2 is {dt}")
assert dt > 1
assert dt < 2
