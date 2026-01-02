import ast
from typing import Dict, List


def _get_function_signature(node: ast.FunctionDef) -> str:
    """Generate function signature string"""
    args = []
    for arg in node.args.args:
        args.append(arg.arg)
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")
    return f"def {node.name}({', '.join(args)})"


def extract_python_symbols(source_code: str, filename: str) -> List[Dict]:
    """
    Extract functions and classes from Python source code using AST.

    Args:
        source_code: Python source code as string
        filename: Name of the file (for error reporting)

    Returns:
        List of dictionaries containing symbol information
    """
    symbols = []
    try:
        tree = ast.parse(source_code, filename=filename)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                symbols.append(
                    {
                        "name": node.name,
                        "type": "function",
                        "line_start": node.lineno,
                        "line_end": node.end_lineno or node.lineno,
                        "signature": _get_function_signature(node),
                    }
                )
            elif isinstance(node, ast.ClassDef):
                symbols.append(
                    {
                        "name": node.name,
                        "type": "class_",
                        "line_start": node.lineno,
                        "line_end": node.end_lineno or node.lineno,
                        "signature": f"class {node.name}",
                    }
                )
    except SyntaxError as e:
        print(f"Syntax error in {filename}: {e}")
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
    return symbols
