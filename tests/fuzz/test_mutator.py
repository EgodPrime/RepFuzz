from repfuzz.mutator import *


def test_mutate_int():
    a = 20
    b = mutate_int(a)
    assert isinstance(b, int) and b != a


def test_mutate_float():
    a = 20.5
    b = mutate_float(a)
    assert isinstance(b, float) and b != a


def test_mutate_complex():
    a = 2 + 3j
    b = mutate_complex(a)
    assert isinstance(b, complex) and b != a


def test_mutate_bool():
    a = True
    b = mutate_bool(a)
    assert isinstance(b, bool) and b != a


def test_mutate_str():
    a = "hello"
    b = mutate_str(a)
    assert isinstance(b, str) and b != a


def test_mutate_bytes():
    a = b"hello"
    b = mutate_bytes(mutate_bytes(a))
    assert isinstance(b, bytes) and b != a

    a = b""
    b = mutate_bytes(a)
    assert isinstance(b, bytes)


def test_mutate_list():
    a = [1, 2, 3]
    b = mutate_list(a)
    assert isinstance(b, list) and b != a


def test_mutate_tuple():
    a = (1, 2, 3)
    b = mutate_tuple(a)
    assert isinstance(b, tuple) and b != a


def test_mutate_set():
    a = {1, 2, 3}
    b = mutate_set(a)
    assert isinstance(b, set) and b != a


def test_mutate_frozenset():
    a = frozenset({1, 2, 3})
    b = mutate_frozenset(mutate_frozenset(a))
    assert isinstance(b, frozenset) and b != a


def test_mutate_bytearray():
    a = bytearray([1, 2, 3])
    b = mutate_bytearray(a)
    assert isinstance(b, bytearray) and b != a


def test_mutate_dict():
    a = {"a": 1, "b": 2}
    b = mutate_dict(a)
    assert isinstance(b, dict)
    c = False
    for key in a.keys():
        if a[key] != b[key]:
            c = True
            break
    assert c


def test_mutate_instance():
    class A:
        def __init__(self) -> None:
            self.f1: int = 2
            self.f2: float = 3
            self.f3: str = "f3"

        def __eq__(self, value) -> bool:
            return self.f1 == value.f1 and self.f2 == value.f2 and self.f3 == value.f3  # type: ignore

    a = A()
    b = mutate_instance(a)
    assert isinstance(b, A)
    assert a != b


def test_mutate_param_list():
    a = [
        1,
        "",
        "s",
        "sss",
        b"bb",
        [2, 3, "s"],
        (
            1,
            2,
        ),
        {3, 4, "s"},
    ]
    b = mutate_param_list(a)
    assert len(a) == len(b)
    mutate_param_list([])
