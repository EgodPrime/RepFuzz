import json

from attrs import Factory, asdict, define, field, validators


def full_name_validator(instance, attribute, value):
    return len(value) > 2 and "." in value


class Dictable:
    def to_dict(self):
        return asdict(self)


@define
class ClassInfo(Dictable):
    full_name = field(type=str, validator=full_name_validator)
    type = field(type=str, validator=validators.in_({"c", "py"}))
    source = field(type=str, default="")
    doc = field(type=str, default="")


@define
class Argument(Dictable):
    name = field(type=str, default="")
    type = field(type=str, default="unknown")
    example_value_list = field(type=list, default=Factory(list))


@define
class API(Dictable):
    full_name = field(type=str, validator=full_name_validator)
    type = field(type=str, default="")
    source = field(type=str, default="")
    doc = field(type=str, default="")
    num_normal_arg = field(type=int, default=0)
    num_kwonly_arg = field(type=int, default=0)
    normal_arg_list = field(type=list[Argument], default=Factory(list))
    kwonly_arg_list = field(type=list[Argument], default=Factory(list))


def adapt_API(api: API) -> tuple:
    normal_arg_list = [arg.to_dict() for arg in api.normal_arg_list]
    kwonly_arg_list = [arg.to_dict() for arg in api.kwonly_arg_list]
    return (
        api.full_name,
        api.type,
        api.source,
        api.doc,
        api.num_normal_arg,
        api.num_kwonly_arg,
        json.dumps(normal_arg_list).encode("utf-8"),
        json.dumps(kwonly_arg_list).encode("utf-8"),
    )


def convert_API(api_sql: tuple) -> API:
    normal_arg_list = json.loads(api_sql[6].decode("utf-8"))
    normal_arg_list = [Argument(**arg) for arg in normal_arg_list]
    kwonly_arg_list = json.loads(api_sql[7].decode("utf-8"))
    kwonly_arg_list = [Argument(**arg) for arg in kwonly_arg_list]
    return API(
        full_name=api_sql[0],
        type=api_sql[1],
        source=api_sql[2],
        doc=api_sql[3],
        num_normal_arg=api_sql[4],
        num_kwonly_arg=api_sql[5],
        normal_arg_list=normal_arg_list,
        kwonly_arg_list=kwonly_arg_list,
    )
