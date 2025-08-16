import copy
import random
from typing import Any, Dict, FrozenSet, Iterable, List, Set, Tuple

from repfuzz.mutate import mutate_bytes, mutate_float, mutate_int, mutate_str

VALUE_TYPES = [
    (int, "int"),
    (float, "float"),
    (complex, "complex"),
    (bool, "bool"),
    (str, "str"),
    (bytes, "bytes"),
    (List, "list"),
    (Tuple, "tuple"),
    (Set, "set"),
    (FrozenSet, "frozenset"),
    (Dict, "dict"),
    (object, "instance"),
]


def get_type(old_val) -> str:
    for type_, val in VALUE_TYPES:
        if isinstance(old_val, type_):  # type: ignore
            return val
    raise ValueError(f"Unknown value type {old_val}")


def mutate_auto(old_val):
    if old_val is None:
        return None
    if isinstance(old_val, object) and type(old_val) is type(object):
        return old_val
    type_ = get_type(old_val)
    func_name = f"mutate_{type_}"
    func = globals()[func_name]
    return func(old_val)


def mutate_complex(old_val: complex) -> complex:
    new_real = mutate_float(old_val.real)
    new_imag = mutate_float(old_val.imag)
    new_val = complex(new_real, new_imag)
    return new_val


def mutate_bool(old_val: bool) -> bool:
    return not old_val


def mutate_list_clip(old_val: list) -> list:
    a = len(old_val)
    if a <= 1:
        return old_val

    b = random.randint(0, a)
    c = random.randint(0, a)
    while b == c:
        c = random.randint(0, a)
    if b > c:
        tmp = b
        b = c
        c = tmp
    return old_val[b:c]


def mutate_list_strict_clip(old_val: list) -> list:
    a = len(old_val)
    if a <= 1:
        return old_val
    b = 0
    c = a
    while abs(b - c) == a:
        b = random.randint(0, a)
        c = random.randint(0, a)
        while b == c:
            c = random.randint(0, a)
    if b > c:
        tmp = b
        b = c
        c = tmp
    return old_val[b:c]


def mutate_list_dup(old_val: list) -> list:
    new_val = old_val * random.randint(2, 10)
    MAX_LEN = 100000
    new_val = new_val[:MAX_LEN]
    return new_val


def mutate_list_expand(old_val: list) -> list:
    a = len(old_val)
    if a == 0:
        return []
    t = random.choice(old_val)
    new_t = mutate_auto(t)
    new_val = copy.deepcopy(old_val)
    new_val.append(new_t)
    return new_val


def mutate_list_random_one(old_val: list) -> list:
    a = len(old_val)
    if a <= 1:
        return old_val
    b = random.randint(0, a - 1)
    new_val = mutate_auto(old_val[b])
    return old_val[:b] + [new_val] + old_val[b + 1 :]


def mutate_list(old_val: list) -> list:
    mt = random.choice(
        [
            mutate_list_strict_clip,
            mutate_list_dup,
            mutate_list_random_one,
            mutate_list_expand,
        ]
    )
    return mt(old_val)


def mutate_tuple(old_val: tuple) -> tuple:
    return tuple(mutate_list(list(old_val)))


def mutate_bytearray(old_val: bytearray) -> bytearray:
    tmp_val = list(old_val)
    new_val = [min(max(0, x), 255) for x in mutate_list(tmp_val)]
    return bytearray(new_val)


def mutate_set(old_val: set) -> set:
    mt = random.choice([mutate_list_strict_clip, mutate_list_random_one, mutate_list_expand])
    return set(mt(list(old_val)))


def mutate_frozenset(old_val: frozenset) -> frozenset:
    return frozenset(mutate_set(set(old_val)))


def mutate_dict(old_val: dict) -> dict:
    new_val = copy.deepcopy(old_val)
    keys = list(new_val.keys())
    if len(keys) == 0:
        return old_val
    mt_key = random.choice(keys)
    new_val[mt_key] = mutate_auto(new_val[mt_key])
    return new_val


def mutate_instance(old_val: object) -> object:
    try:
        new_val = copy.deepcopy(old_val)
        members = dir(new_val)
        members = [x for x in members if not x.startswith("__")]
        if len(members) == 0:
            return old_val
        mt_member = random.choice(members)
        new_member = mutate_auto(getattr(new_val, mt_member))
        setattr(new_val, mt_member, new_member)
    except Exception:
        pass
    return new_val


def mutate_param_list(old_val: List[Dict]) -> List:
    a = len(old_val)
    if a <= 1:
        return old_val
    new_val = copy.deepcopy(old_val)
    mt_num = random.randint(0, a) + 1
    full_idx = list(range(a))
    mt_idx = random.choices(full_idx, k=mt_num)
    for i in mt_idx:
        new_val[i] = mutate_auto(new_val[i])
    return new_val
