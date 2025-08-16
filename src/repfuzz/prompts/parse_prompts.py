from repfuzz.config import PARSE


def get_user_function_prompt_C(source, docstring, arg_name) -> str:
    prompt = f"""
According to the source:
{source}
and the docstring:                                                                                                                              
{docstring},
please infer the type and possible values for the argument {arg_name}. 

Your output should be in valid JSON format, with the following structure:
- A "name" key with the value set to the argument name.
- A "type" key with the inferred type of the argument.
- An "example_value_list" key with an array of strings representing possible values for the argument.

If the type or possible values cannot be determined from the provided information, you should try guessing one.

Here is an example of the expected output format:
<START>
{{
    "name": "name of the argument",
    "type": "the inferred type",
    "example_value_list": ["possible value 1", "possible value 2", ...]
}}
<END>

Now, please provide your inference based on the given information:
<START>
{{
    "name": "{arg_name}",
"""
    return prompt


def get_user_function_prompt_NT(source, docstring, arg_name) -> str:
    prompt = f"""
According to the source:
{source}
and the docstring:                                                                                                                              
{docstring},
please infer the type and possible values for the argument {arg_name}. 

Here is an example of the expected output format:
<START>
{{
    "name": "name of the argument",
    "type": "the inferred type",
    "example_value_list": ["possible value 1", "possible value 2", ...]
}}
<END>

Now, please provide your inference based on the given information:
<START>
{{
    "name": "{arg_name}",
"""
    return prompt


def get_user_function_prompt_NS(source, docstring, arg_name) -> str:
    prompt = f"""
According to the source:
{source}
and the docstring:                                                                                                                              
{docstring},
please infer the type and possible values for the argument {arg_name}. 

Your output should be in valid JSON format, with the following structure:
- A "name" key with the value set to the argument name.
- A "type" key with the inferred type of the argument.
- An "example_value_list" key with an array of strings representing possible values for the argument.

If the type or possible values cannot be determined from the provided information, you should try guessing one.

Now, please provide your inference based on the given information:
<START>
{{
    "name": "{arg_name}",
"""
    return prompt


def get_builtin_function_prompt_C(pyi_def, docstring) -> str:
    prompt = f"""
Positional-Only Argument (posonlyarg): Positional-only arguments would be placed before a `/`. 
Keyword-Only Argument (kwonlyarg): Keyword-only arguments would be placed after a `*`.
Positional-or-Keyword Arguments (posorkwarg): Arguments between `/` and `*` are positional-or-keyword arguments. If the function has no `/` or `*`, all arguments are positional-or-keyword arguments. 

According to the above function definition:
{pyi_def}
and the docstring:
{docstring}
output there are how many normal arguments and keyword-only arguments, and their types and example values.

Your output should be in valid JSON format, with the following structure:
- A "name" key with the value set to the argument name.
- A "type" key with the inferred type of the argument.
- An "example_value_list" key with an array of strings representing possible values for the argument.

If the type or possible values cannot be determined from the provided information, you should try guessing one.

Here is an example of the expected output format:
<START>
{{
    "normal_arg_list":[
        {{
            "name" : "name of the argument",
            "type" : "the type you think",
            "example_value_list" : ["possible value 1", "possible value 2", ...]
        }},
        ...
    ],
    "kwonly_arg_list:[...]
}}
<END>

Now, please provide your inference based on the given information:
<START>
"""
    return prompt


def get_builtin_function_prompt_NT(pyi_def, docstring) -> str:
    prompt = f"""
According to the above function definition:
{pyi_def}
and the docstring:
{docstring}
output there are how many normal arguments and keyword-only arguments, and their types and example values.


Here is an example of the expected output format:
<START>
{{
    "normal_arg_list":[
        {{
            "name" : "name of the argument",
            "type" : "the type you think",
            "example_value_list" : ["possible value 1", "possible value 2", ...]
        }},
        ...
    ],
    "kwonly_arg_list:[...]
}}
<END>

Now, please provide your inference based on the given information:
<START>
"""
    return prompt


def get_builtin_function_prompt_NS(pyi_def, docstring) -> str:
    prompt = f"""
Positional-Only Argument (posonlyarg): Positional-only arguments would be placed before a `/`. 
Keyword-Only Argument (kwonlyarg): Keyword-only arguments would be placed after a `*`.
Positional-or-Keyword Arguments (posorkwarg): Arguments between `/` and `*` are positional-or-keyword arguments. If the function has no `/` or `*`, all arguments are positional-or-keyword arguments. 

According to the above function definition:
{pyi_def}
and the docstring:
{docstring}
output there are how many normal arguments and keyword-only arguments, and their types and example values.

Your output should be in valid JSON format, with the following structure:
- A "name" key with the value set to the argument name.
- A "type" key with the inferred type of the argument.
- An "example_value_list" key with an array of strings representing possible values for the argument.

If the type or possible values cannot be determined from the provided information, you should try guessing one.

Now, please provide your inference based on the given information:
<START>
"""
    return prompt


get_user_function_prompt = globals()[f"get_user_function_prompt_{PARSE.user_function_prompt_option}"]
get_builtin_function_prompt = globals()[
    f"get_builtin_function_prompt_{PARSE.builtin_function_prompt_option}"
]
