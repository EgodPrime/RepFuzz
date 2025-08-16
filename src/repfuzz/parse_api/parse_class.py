import inspect

from repfuzz.database.models import ClassInfo
from repfuzz.tools.tools import remove_docstr


def parse_class(obj: type) -> ClassInfo:
    full_name = f"{obj.__module__}.{obj.__name__}"
    _type = "c"
    source = ""
    doc = ""
    try:
        source = inspect.getsource(obj)
        source = remove_docstr(source)
        _type = "py"
    except Exception:
        pass

    try:
        doc = obj.__doc__ if obj.__doc__ is not None else ""
    except Exception:
        pass

    return ClassInfo(full_name, _type, source, doc)
