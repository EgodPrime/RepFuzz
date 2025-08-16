import importlib
import inspect
import json
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType
from typing import Any, Callable, List

from colorama import Fore

from repfuzz.database.models import Argument
from repfuzz.database.sqlite_proxy import get_or_create_db, insert_into_api
from repfuzz.llm import async_generate
from repfuzz.prompts.parse_prompts import (
    get_builtin_function_prompt,
    get_user_function_prompt,
)
from repfuzz.tools.tools import find_function_definition_in


class APIParser:
    def __init__(self, api: Callable) -> None:
        self.api = api
        self.db_conn = get_or_create_db(api.__module__.split(".")[0])
        self.full_name = f"{api.__module__}.{api.__name__}"
        self.type: str = ""
        self.source = ""
        self.doc = ""
        self.num_normal_arg: int = 0
        self.num_kwonly_arg: int = 0
        self.normal_arg_list: List[Argument] = []
        self.kwonly_arg_list: List[Argument] = []

    def save_to_db(self):
        insert_into_api(self.db_conn, self)

    async def parse(self):
        self.parse_type()
        self.parse_source()
        if "exit(" in self.source:
            raise RuntimeError(f"{self.full_name} contains exit() function")
        if "input(" in self.source:
            raise RuntimeError(f"{self.full_name} contains input() function")
        self.parse_doc()
        await self.parse_arguments()

    def parse_type(self):
        if isinstance(self.api, FunctionType):
            self.type = str(FunctionType)
        elif isinstance(self.api, BuiltinFunctionType):
            self.type = str(BuiltinFunctionType)
        elif isinstance(self.api, BuiltinMethodType):
            self.type = str(BuiltinMethodType)
        elif isinstance(self.api, MethodType):
            self.type = str(MethodType)
        else:
            raise TypeError("Unknown type of API")

    def parse_source(self):
        raise NotImplementedError

    def parse_doc(self):
        try:
            self.doc = self.api.__doc__
        except Exception:
            self.doc = ""

    async def parse_arguments(self):
        raise NotImplementedError

    def to_dict(self) -> dict:
        res: dict[str, Any] = {}
        res["full_name"] = self.full_name
        res["type"] = str(self.type)
        res["source"] = self.source
        res["doc"] = self.doc
        res["num_normal_arg"] = self.num_normal_arg
        res["num_kwonly_arg"] = self.num_kwonly_arg
        res["normal_arg_list"] = [arg.to_dict() for arg in self.normal_arg_list]
        res["kwonly_arg_list"] = [arg.to_dict() for arg in self.kwonly_arg_list]
        return res


class FunctionParser(APIParser):
    """
    User defined function alwasy has source and docstring.

    And its argument information can be directly accessed.
    """

    def parse_source(self):
        self.source = inspect.getsource(self.api)

    async def parse_arguments(self):
        self.parse_arg_num_and_name()
        print(
            f"{Fore.BLUE}Start parsing user-define function {self.full_name}({self.num_normal_arg} normal, {self.num_kwonly_arg} kwonly){Fore.RESET}"
        )
        await self.parse_arg_type()
        print(f"{Fore.GREEN}Finished parsing user-define function {self.full_name}{Fore.RESET}")

    def parse_arg_num_and_name(self):
        func: FunctionType = self.api
        code = func.__code__
        self.num_normal_arg = code.co_argcount
        self.num_kwonly_arg = code.co_kwonlyargcount
        var_names = code.co_varnames
        idx = 0
        for _ in range(self.num_normal_arg):
            self.normal_arg_list.append(Argument(name=var_names[idx]))
            idx += 1
        for _ in range(self.num_kwonly_arg):
            self.kwonly_arg_list.append(Argument(name=var_names[idx]))
            idx += 1

    async def parse_arg_type(self):
        for idx, arg in enumerate(self.normal_arg_list):
            self.normal_arg_list[idx] = await self._parse_one_arg_type(arg.name)
        for idx, arg in enumerate(self.kwonly_arg_list):
            self.kwonly_arg_list[idx] = await self._parse_one_arg_type(arg.name)

    async def _parse_one_arg_type(self, arg_name: str) -> Argument:
        prompt = get_user_function_prompt(self.source, self.doc, arg_name)
        for _ in range(20):
            res = await async_generate(prompt)
            res = f'{{\n    "name": "{arg_name}",\n' + res
            try:
                res_dict: dict = json.loads(res)
                try:
                    arg = Argument(**res_dict)
                    return arg
                except Exception as e:
                    pass
            except Exception as e:
                pass
        raise Exception("Parse Failed")


class BuiltinFunctionParser(FunctionParser):
    """
    Builtin function does not have source.

    But most of them have docstring.

    Signature is not always available.

    A formal library offers a .pyi file which can be used to infer the argument information.
    """

    def parse_source(self):
        return ""

    async def parse_arguments(self):
        root_library = self.api.__module__.split(".")[0]
        target = importlib.import_module(root_library)
        pyi_def = find_function_definition_in(target.__path__[0], self.api.__name__)
        if pyi_def == None and self.doc == "":
            raise RuntimeError(f"{self.full_name} does not have any source or docstring.")
        prompt = get_builtin_function_prompt(pyi_def, self.doc)
        print(f"{Fore.BLUE}Start parsing builtin function {self.full_name}{Fore.RESET}")
        for _ in range(20):
            res = await async_generate(prompt)
            try:
                res = json.loads(res)
                normal_arg_list = res["normal_arg_list"]
                kwonly_arg_list = res["kwonly_arg_list"]
                try:
                    normal_arg_list = [Argument(**x) for x in normal_arg_list]
                    kwonly_arg_list = [Argument(**x) for x in kwonly_arg_list]
                    self.num_normal_arg = len(normal_arg_list)
                    self.num_kwonly_arg = len(kwonly_arg_list)
                    self.normal_arg_list = normal_arg_list
                    self.kwonly_arg_list = kwonly_arg_list
                    print(
                        f"{Fore.GREEN}Finished parsing builtin function {self.full_name}{Fore.RESET}"
                    )
                    return
                except Exception:
                    pass
            except Exception:
                pass
        raise Exception("Parse Failed")


async def parse_api(api: Callable):
    if isinstance(api, FunctionType):
        parser = FunctionParser(api)
    elif isinstance(api, BuiltinFunctionType):
        parser = BuiltinFunctionParser(api)
    elif isinstance(api, BuiltinMethodType):
        raise NotImplementedError
    elif isinstance(api, MethodType):
        raise NotImplementedError
    else:
        raise TypeError("Unknown type of API")
    await parser.parse()
    parser.save_to_db()
