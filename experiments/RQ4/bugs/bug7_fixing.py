import numpy as np

x = 1
shape = [1] * 136  # 0-135 is safe

# np.lib.stride_tricks.as_strided(x, shape=shape)


class DummyArray:
    """Dummy object that just exists to hang __array_interface__ dictionaries
    and possibly keep alive a reference to a base array.
    """

    def __init__(self, interface, base=None):
        self.__array_interface__ = interface
        self.base = base


x = np.array(x, copy=None, subok=False)
interface = dict(x.__array_interface__)
interface["shape"] = tuple(shape)
da = DummyArray(interface=interface, base=x)
np.asanyarray(da)

"""
Segmentation fault (core dumped)

Thread 1 "python" received signal SIGSEGV, Segmentation fault.
0x0000000000000001 in ?? ()
(gdb) bt
#0  0x0000000000000001 in ?? ()
#1  0x00007ffc81825b7c in ?? ()
#2  0x00007ffc81825b68 in ?? ()
#3  0x00007f12f2ef2780 in ?? ()
#4  0x0000000000000000 in ?? ()


Traceback (most recent call last):
  File "/root/auto-pyapi-fuzzer/bugs/bug7.py", line 20, in <module>
    np.asanyarray(da)
ValueError: number of dimensions must be within [0, 64]
"""
