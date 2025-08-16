import os
import re


def remove_docstr(code: str) -> str:
    lines = code.split("\n")
    res = ""
    indocstr = False
    docstr_style = ""
    for i, line in enumerate(lines):
        if line.strip().startswith("'''") or line.strip().startswith('"""'):
            if not indocstr:
                if line.strip().startswith("'''"):
                    docstr_style = "'''"
                else:
                    docstr_style = '"""'
                indocstr = True
            else:
                if line.strip().startswith(docstr_style):
                    indocstr = False
            continue
        if not indocstr:
            res += f"{line}\n"
    return res


def clean_api_call(api_call: str) -> str:
    """
    `api_call` is a python code.
    This function remove all print and comments in `api_call`.
    """
    lines = api_call.split("\n")
    clean_lines = []

    in_multiline_comment_single = False
    in_multiline_comment_double = False

    for line in lines:
        # Check if the line starts a multi-line comment
        if line.strip().startswith("'''"):
            in_multiline_comment_single = not in_multiline_comment_single
        if line.strip().startswith('"""'):
            in_multiline_comment_double = not in_multiline_comment_double

        if in_multiline_comment_single or in_multiline_comment_double:
            continue

        # Check if the line is a print statement or a single-line comment
        if line.lstrip().startswith("print("):
            continue
        if line.lstrip().startswith("#"):
            continue

        clean_lines.append(line)

    # Join the non-clean lines back into a single string
    return "\n".join(clean_lines)


def find_all_pyi_files(path: str) -> list[str]:
    res = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".pyi"):
                res.append(os.path.join(root, file))
        for d in dirs:
            res.extend(find_all_pyi_files(os.path.join(root, d)))
    return res


def find_function(func_name: str, content: str) -> str | None:
    pattern = r"def\s+" + func_name + r"\s*\([^)]*\)[^:]*:\s*..."
    match = re.search(pattern, content, flags=re.MULTILINE)
    if match:
        return match.group(0)
    return None


def find_function_definition_from_pyis(pyi_files: list[str], api_name: str) -> str | None:
    res = None
    for pyi_file in pyi_files:
        f = open(pyi_file, "r")
        find = find_function(api_name, f.read())
        f.close()
        if find:
            res = find
            break
    return res


def find_function_definition_in(path: str, api_name: str) -> str | None:
    pyi_files = find_all_pyi_files(path)
    return find_function_definition_from_pyis(pyi_files, api_name)
