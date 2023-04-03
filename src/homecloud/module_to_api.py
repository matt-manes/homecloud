import argparse
import importlib
import importlib.util
import inspect
import sys
from pathier import Pathier
from typing import Any

import black

root = Pathier(__file__).parent

""" Generate client functions from a module's functions."""


def load_module_from_file(path: Pathier) -> Any:
    """Load a module from a local file."""
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def get_module(module: str | Pathier) -> Any:
    """Load and return a module.

    :param module: Either the name of an installed package
    or a Path object pointing to a .py file"""
    try:
        if type(module) == str:
            return importlib.import_module(module)
        else:
            return load_module_from_file(module)
    except Exception as e:
        print(e)
        print(f"Could not load {module}")


def get_functions(module) -> list[tuple]:
    """Return a list of public functions.
    Each element is a tuple containing the
    function name, value, and docstring."""
    functions = []
    for function, value in inspect.getmembers(module):
        if inspect.isclass(value):
            for class_function, class_value in inspect.getmembers(value):
                if inspect.isfunction(class_value):
                    functions.append(
                        (class_function, class_value, inspect.getdoc(class_value))
                    )
        elif inspect.isfunction(value):
            functions.append((function, value, inspect.getdoc(value)))
    origin = Pathier(importlib.util.find_spec(module.__name__).origin)
    # Local packages include functions from built in modules they import
    if not ("Lib" and "Python" and "site-packages" in origin.parts):
        source = inspect.getsource(module)
        functions = [
            function for function in functions if f"def {function[0]}" in source
        ]
    return [function for function in functions if not function[0].startswith("_")]


def format_definition(function: tuple[str, Any]) -> str:
    """Return a function definition string from
    a tuple containing the function name and it's value."""
    params = str(inspect.signature(function[1]))
    if "(self" not in params:
        params = params.replace("(", "(self, ", 1)
    return f"def {function[0]}{params}:"


def format_request(
    function_parameters: dict | list[str],
    method: str = None,
    resource: str = None,
) -> str:
    """Format and return the send_request line of the function.

    :param function_parameters: An iterable of parameters
    to be sent in the request body.

    :param method: Replace '$METHOD' with parameter value.

    :param resource: Replace '$RESOURCE' with parameter value."""
    data = ", ".join(
        [f'"{param}": {param}' for param in function_parameters if param != "self"]
    )
    request = f'response = self.send_request("$METHOD", "$RESOURCE", data={{{data}}})'
    if method:
        request = request.replace("$METHOD", method)
    if resource:
        request = request.replace("$RESOURCE", resource)
    return request


def format_return(return_annotation: Any) -> str:
    """Format the function return line.

    :param return_annotation: The return type(s) of the function."""
    return_ = "return "
    if return_annotation == inspect._empty:
        return_ += "response"
    elif return_annotation not in [int, float, str, bool]:
        return_ += "json.loads(response.text)"
    else:
        return_ += "response.text"
    return return_


def format_function(
    decorator: str,
    definition: str,
    doc: str,
    request: str,
    return_: str,
    indent_level: int,
    indent_ch: str,
) -> str:
    """Format function from it's parts."""
    function = ""
    indent = indent_ch * indent_level
    line = lambda s: f"{indent}{s}\n"
    for part in [decorator, definition]:
        function += line(part)
    # Indent another level for the function body
    indent += indent_ch
    for part in [doc, request, return_]:
        function += line(part)
    return function


def generate_client_functions(
    functions: list[tuple],
    default_method: str = None,
    resource_parent: str = None,
    indent_level: int = 1,
    indent_ch: str = " " * 4,
) -> str:
    """Generate client functions from a list of functions
    where each element is a tuple containing the function
    name, the function value, and the function's docstring.

    :param method: Replace '$METHOD' with parameter value.
    If not provided, function names with 'get' in them will
    replace their instance of '$METHOD' with 'get'
    and methods with no return annotation will
    have theirs replaced with 'post' .

    :param resource_parent: The resource path will be determined by the function name.
    This value will be prepended to it.
    e.g. For a module function "get_rows" and a resource_parent "database/users",
    the endpoint the client function will request is "/database/users/get-rows" .

    :param indent_level: The indent level of the function.
    If using the generated client file, this should be left as default.

    :param indent_ch: The indentation character to use.
    Default is four spaces."""
    client_functions = []

    for function in functions:
        # Reset method for each iteration
        method = default_method
        sig = inspect.signature(function[1])
        decorator = "@on_fail"
        definition = format_definition(function)
        # If no return annotation, make return type request.Response
        if sig.return_annotation == inspect._empty:
            # Reverse the definition so only the last ':' occurence is replaced
            # then reverse it back.
            definition = definition[::-1].replace(":", "->requests.Response:"[::-1], 1)[
                ::-1
            ]
        doc = f'""" {function[2] if not None else "No docstring found."} """'
        resource = f"/{function[0].replace('_','-')}"
        if resource_parent:
            resource = f"/{resource_parent}{resource}"
        if not method:
            if "get" in definition.lower():
                method = "get"
            elif sig.return_annotation == inspect._empty:
                method = "post"
        request = format_request(
            sig.parameters,
            method,
            resource,
        )
        return_ = format_return(sig.return_annotation)
        client_functions.append(
            format_function(
                decorator, definition, doc, request, return_, indent_level, indent_ch
            )
        )
    return client_functions


def append_to_client(client_path: Pathier, client_functions: list[str]):
    """Append client_functions to client file if a function
    with the same name doesn't already exist."""
    content = client_path.read_text()
    content += "\n" + "\n".join(
        [
            function
            for function in client_functions
            if function[: function.find("(")].strip() not in content
        ]
    )
    try:
        client_path.write_text(black.format_str(content, mode=black.Mode()))
    except Exception as e:
        print(e)
        client_path.write_text(content)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "module",
        type=str,
        help=""" The name of the installed module or a path to .py file 
        to generate functions for. """,
    )

    parser.add_argument(
        "-m",
        "--method",
        type=str,
        default=None,
        help=""" Replace method placeholders in generated functions
        with this string. If None, any function with 'get' in the name
        will have their method placeholder replaced with 'get'.""",
    )

    parser.add_argument(
        "-r",
        "--resource_parent",
        type=str,
        default=None,
        help="""The resource path will be determined by the function name.
        This value will be prepended to it.
        e.g. For a module function "get_rows" and a resource_parent "database/users",
        the endpoint the client function will request is "/database/users/get-rows" .""",
    )

    parser.add_argument(
        "-il",
        "--indent_level",
        type=int,
        default=1,
        help=""" The indent level to use for the generated
        functions when writing them to the client file.""",
    )

    parser.add_argument(
        "-ic",
        "--indent_ch",
        type=str,
        default=" " * 4,
        help=""" The character to use for indentation.
        Default is four spaces.""",
    )

    parser.add_argument(
        "-c",
        "--client",
        type=str,
        default=None,
        help=""" The path to a homecloud generated client file to append
        the generated functions to.
        If None, the current working directory will be scanned for one.""",
    )

    parser.add_argument(
        "-f",
        "--functions",
        type=str,
        default=None,
        nargs="*",
        help=""" A list of functions to add.
        If None, every function in the module file
        will be added.""",
    )

    args = parser.parse_args()
    if not args.client:
        try:
            args.client = [
                file
                for file in Pathier.cwd().glob("*_client.py")
                if "HomeCloudClient" in file.read_text()
            ][0]
        except Exception as e:
            raise FileNotFoundError(
                "Could not find an appropriate client file in the current directory."
            )
    if args.module.strip().endswith(".py"):
        args.module = Pathier(args.module)
        if not args.module.is_absolute():
            args.module = Pathier.cwd() / args.module

    return args


def main(args: argparse.Namespace = None):
    if not args:
        args = get_args()
    module = get_module(args.module)
    module_functions = get_functions(module)
    if args.functions:
        module_functions = [
            function for function in module_functions if function[0] in args.functions
        ]
    client_functions = generate_client_functions(
        module_functions,
        args.method,
        args.resource_parent,
        args.indent_level,
        args.indent_ch,
    )
    append_to_client(args.client, client_functions)


if __name__ == "__main__":
    main(get_args())
