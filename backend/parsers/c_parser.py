import uuid
from typing import Dict, List

try:
    from tree_sitter_languages import get_language, get_parser

    parser = get_parser("c")
    language = get_language("c")
except Exception:
    import tree_sitter_c as tsc
    from tree_sitter import Language, Parser

    language = Language(tsc.language())
    parser = Parser(language)


def get_function_name(declarator_node, source_code: bytes) -> str:
    """Recursively extract function name from declarator"""
    if declarator_node.type == "identifier":
        return source_code[
            declarator_node.start_byte : declarator_node.end_byte
        ].decode("utf-8")

    declarator = declarator_node.child_by_field_name("declarator")
    if declarator:
        return get_function_name(declarator, source_code)

    return "unknown"


def extract_symbols(node, source_code: bytes, symbols: List[Dict]):
    """Recursively extract symbols from AST"""

    if node.type == "function_definition":
        declarator = node.child_by_field_name("declarator")
        if declarator:
            name = get_function_name(declarator, source_code)
            full_text = source_code[node.start_byte : node.end_byte].decode(
                "utf-8", errors="ignore"
            )
            first_line = full_text.split("\n")[0]
            signature = (
                (first_line[:100] + "...")
                if len(first_line) > 100
                else (first_line + " {...}")
            )

            symbols.append(
                {
                    "name": name,
                    "type": "function",
                    "signature": signature,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                }
            )

    elif node.type == "struct_specifier":
        name_node = node.child_by_field_name("name")
        if name_node:
            name = source_code[name_node.start_byte : name_node.end_byte].decode(
                "utf-8"
            )
            symbols.append(
                {
                    "name": name,
                    "type": "class_",
                    "signature": f"struct {name}",
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                }
            )

    elif node.type == "enum_specifier":
        name_node = node.child_by_field_name("name")
        if name_node:
            name = source_code[name_node.start_byte : name_node.end_byte].decode(
                "utf-8"
            )
            symbols.append(
                {
                    "name": name,
                    "type": "class_",
                    "signature": f"enum {name}",
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                }
            )

    for child in node.children:
        extract_symbols(child, source_code, symbols)


def parse_c_file(file_path: str, repository_id: str | None = None) -> List[Dict]:
    """Parse C file and extract symbols"""
    with open(file_path, "rb") as f:
        source_code = f.read()

    tree = parser.parse(source_code)
    symbols = []
    extract_symbols(tree.root_node, source_code, symbols)

    if repository_id:
        for symbol in symbols:
            symbol["symbol_id"] = str(uuid.uuid4())
            symbol["file_path"] = file_path
            symbol["repository_id"] = repository_id

    return symbols


def extract_c_symbols(source_code: str, filename: str = "") -> List[Dict]:
    """Extract symbols from C source code string"""
    source_bytes = source_code.encode("utf-8")
    tree = parser.parse(source_bytes)
    symbols = []
    extract_symbols(tree.root_node, source_bytes, symbols)
    return symbols
