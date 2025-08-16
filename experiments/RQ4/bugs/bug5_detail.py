args = [1.0471, 2, True, True, "k", 2048, int(1e5), 0, 0]

import numpy as np
from numpy._core.multiarray import dragon4_positional


def _none_or_positive_arg(x, name):
    if x is None:
        return -1
    if x < 0:
        raise ValueError("{} must be >= 0".format(name))
    return x


def format_float_positional(
    x,
    precision=None,
    unique=True,
    fractional=True,
    trim="k",
    sign=False,
    pad_left=None,
    pad_right=None,
    min_digits=None,
):
    precision = _none_or_positive_arg(precision, "precision")
    pad_left = _none_or_positive_arg(pad_left, "pad_left")
    pad_right = _none_or_positive_arg(pad_right, "pad_right")
    min_digits = _none_or_positive_arg(min_digits, "min_digits")
    if not fractional and precision == 0:
        raise ValueError("precision must be greater than 0 if " "fractional=False")
    if min_digits > 0 and precision > 0 and min_digits > precision:
        raise ValueError("min_digits must be less than or equal to precision")

    print("I'm ok")
    # the dragon4_positional broken!
    return dragon4_positional(
        x,
        precision=precision,
        unique=unique,
        fractional=fractional,
        trim=trim,
        sign=sign,
        pad_left=pad_left,
        pad_right=pad_right,
        min_digits=min_digits,
    )


print("Befor call")
format_float_positional(*args)
print("The Python Interpretor still alive after call")
print("But Segmentation Fault would happen once exit")
"""
Segmentation fault

Thread 1 "python" received signal SIGSEGV, Segmentation fault.
__memset_avx2_erms () at ../sysdeps/x86_64/multiarch/memset-vec-unaligned-erms.S:151
151     ../sysdeps/x86_64/multiarch/memset-vec-unaligned-erms.S: No such file or directory.

dragon4_positional is implemented in _multiarray_umath.*.so
"""
