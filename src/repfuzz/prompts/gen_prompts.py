from repfuzz.config import GENERATION
from repfuzz.database.models import API


def get_gen_prompt_C(api: API):
    top_module = api.full_name.split(".")[0]
    prompt = f"""You are a Python programer.
According to the source:
{api.source}
and docstring:
{api.doc}
and its positional arguments:
{str([x.to_dict() for x in api.normal_arg_list])}
and its keyword-only arguments:
{str([x.to_dict() for x in api.kwonly_arg_list])}
generate a valid python code that calls {api.full_name}.

Note:
- Do not generate any comments.
- Do not generate any `print`
- You should at first create every argument with a variable, then call the target api using them.
- Generate a <END> when you are doen.

An output example is like:
<START>
import {top_module}
from {top_module} import func_a
_a = 2
_b = "world"
_c = "hello"
func_a(_a, _b, c=_c)
<END>

Now start:

<START>
"""
    return prompt


def get_gen_prompt_NT(api: API):
    top_module = api.full_name.split(".")[0]
    prompt = f"""You are a Python programer.
According to the source:
{api.source}
and docstring:
{api.doc}
and its positional arguments:
{str([x.to_dict() for x in api.normal_arg_list])}
and its keyword-only arguments:
{str([x.to_dict() for x in api.kwonly_arg_list])}
generate a valid python code that calls {api.full_name}.

An output example is like:
<START>
import {top_module}
from {top_module} import func_a
_a = 2
_b = "world"
_c = "hello"
func_a(_a, _b, c=_c)
<END>

Now start:

<START>
"""
    return prompt


def get_gen_prompt_NS(api: API):
    top_module = api.full_name.split(".")[0]
    prompt = f"""You are a Python programer.
According to the source:
{api.source}
and docstring:
{api.doc}
and its positional arguments:
{str([x.to_dict() for x in api.normal_arg_list])}
and its keyword-only arguments:
{str([x.to_dict() for x in api.kwonly_arg_list])}
generate a valid python code that calls {api.full_name}.

Note:
- Do not generate any comments.
- Do not generate any `print`
- You should at first create every argument with a variable, then call the target api using them.
- Generate a <END> when you are doen.

Now start:

<START>
"""
    return prompt

def get_gen_prompt_wo_phase1(api: API):
    prompt = f"""You are a Python programer.
Generate an API call for the following API: {api.full_name}.

Note:
- Do not generate any comments.
- Do not generate any `print`
- You should at first create every argument with a variable, then call the target api using them.
- Generate a <END> when you are doen.

Now start:
<START>
"""
    return prompt


get_gen_prompt = globals()[f"get_gen_prompt_{GENERATION.prompt_option}"]
