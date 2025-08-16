from typing import Any, Set


def objjson(obj: object) -> Any:
    return _objjson(obj, set())


def _objjson(obj: Any, memo: Set[int]) -> Any:
    """
    Recursively converts an object into a JSON-serializable object.

    This function is designed to handle recursive objects by tracking their identities
    in the `memo` set.

    Args:
        obj: The object to convert. It can be of any type, including built-in types,
            user-defined classes, and collections (lists, tuples, sets, dicts).
        memo: A set of object identities to prevent infinite recursion.

    Returns:
        The JSON-serializable representation of the `obj`. If the object is already
        JSON-serializable (i.e., its representation does not contain cycles), it is
        returned as is.

    Raises:
        ValueError: If the object contains cycles that cannot be JSON-serialized.
    """
    if isinstance(obj, (str, int, float, complex, bool, bytes, bytearray)) or obj is None:
        return obj

    if id(obj) in memo:
        raise ValueError("Can't jsonify a recursive object")

    memo.add(id(obj))

    if isinstance(obj, (list, tuple, set, frozenset)):
        return [_objjson(elem, memo.copy()) for elem in obj]

    if isinstance(obj, dict):
        return {key: _objjson(val, memo.copy()) for key, val in obj.items()}

    # For generic object
    ret = {".type": type(obj).__name__}

    if hasattr(obj, "__dir__"):
        for attr in dir(obj):
            if not attr.startswith("__"):
                try:
                    val = getattr(obj, attr)
                    if not callable(val):  # Skip methods
                        if isinstance(val, (list, tuple, set, dict)):
                            ret[attr] = _objjson(val, memo.copy())
                        else:
                            ret[attr] = val
                except Exception:
                    pass
    return ret
