import uuid
from typing import Dict, List

from tree_sitter_languages import get_language, get_parser


class CParser:
    """Parser for C programming language"""

    def __init__(self):
        self.parser = get_parser("c")
        self.language = get_language("c")

    def parse_file(self, file_path: str, repository_id: str) -> List[Dict]:
        """Extract symbols from C file"""
        with open(file_path, "rb") as f:
            source_code = f.read()
        tree = self.parser.parse(source_code)
        symbols = []
        self._extract_symbols(
            tree.root_node, source_code, file_path, repository_id, symbols
        )
        return symbols

    def _extract_symbols(
        self,
        node,
        source_code: bytes,
        file_path: str,
        repository_id: str,
        symbols: List[Dict],
    ):
        """Recursively extract C symbols"""
        if node.type == "function_definition":
            name_node = node.child_by_field_name("declarator")
            if name_node:
                func_name = self._get_function_name(name_node, source_code)
                signature = source_code[node.start_byte : node.end_byte].decode(
                    "utf-8", errors="ignore"
                )
                signature_preview = signature.split("\n")[0]
                if len(signature_preview) > 100:
                    signature_preview = signature_preview[:100] + "..."
                else:
                    signature_preview += " {...}"
                symbols.append(
                    {
                        "symbol_id": str(uuid.uuid4()),
                        "name": func_name,
                        "type": "function",
                        "signature": signature_preview,
                        "file_path": file_path,
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "repository_id": repository_id,
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
                        "symbol_id": str(uuid.uuid4()),
                        "name": name,
                        "type": "class_",
                        "signature": f"struct {name}",
                        "file_path": file_path,
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "repository_id": repository_id,
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
                        "symbol_id": str(uuid.uuid4()),
                        "name": name,
                        "type": "class_",
                        "signature": f"enum {name}",
                        "file_path": file_path,
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "repository_id": repository_id,
                    }
                )
        elif node.type == "type_definition":
            for child in reversed(node.children):
                name = source_code[child.start_byte : child.end_byte].decode("utf-8")
                signature = source_code[node.start_byte : node.end_byte].decode(
                    "utf-8", errors="ignore"
                )
                symbols.append(
                    {
                        "symbols_id": str(uuid.uuid4()),
                        "name": name,
                        "type": "variable",
                        "signature": signature.strip(),
                        "file_path": file_path,
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "repository_id": repository_id,
                    }
                )
                break
        for child in node.children:
            self._extract_symbols(child, source_code, file_path, repository_id, symbols)

    def _get_function_name(self, declarator_node, source_code: bytes) -> str:
        """Extract function name from declarator node"""
        if declarator_node.type == "identifier":
            declarator = declarator_node.child_by_field_name("declarator")
            if declarator:
                return self._get_function_name(declarator, source_code)
        elif declarator_node.type == "pointer_declarator":
            declarator = declarator_node.child_by_field_name("declarator")
            if declarator:
                return self._get_function_name(declarator, source_code)
        elif declarator_node.type == "identifier":
            return source_code[
                declarator_node.start_byte : declarator_node.end_byte
            ].decode("utf-8")
        return "unknown"


def extract_c_symbols(source_code: str, filename: str) -> List[Dict]:
    """
    Wrapper function to extract C symbols.
    Compatible with parse_repository.py interface.
    """
    try:
        parser = get_parser("c")
        tree = parser.parse(bytes(source_code, "utf-8"))

        symbols = []

        def extract_from_node(node, source_bytes: bytes):
            if node.type == "function_definition":
                declarator = node.child_by_field_name("declarator")
                func_name = "unknown"

                if declarator:
                    if declarator.type == "function_declarator":
                        name_node = declarator.child_by_field_name("declarator")
                        if name_node:
                            func_name = source_bytes[
                                name_node.start_byte : name_node.end_byte
                            ].decode("utf-8")
                    elif declarator.type == "pointer_declarator":
                        decl = declarator.child_by_field_name("declarator")
                        if decl and decl.type == "function_declarator":
                            name_node = decl.child_by_field_name("declarator")
                            if name_node:
                                func_name = source_bytes[
                                    name_node.start_byte : name_node.end_byte
                                ].decode("utf-8")
                    elif declarator.type == "identifier":
                        func_name = source_bytes[
                            declarator.start_byte : declarator.end_byte
                        ].decode("utf-8")

                full_text = source_bytes[node.start_byte : node.end_byte].decode(
                    "utf-8", errors="ignore"
                )
                first_line = full_text.split("\n")[0].strip()
                if len(first_line) > 100:
                    signature = first_line[:100] + "..."
                else:
                    signature = first_line + " {...}"

                symbols.append(
                    {
                        "name": func_name,
                        "type": "function",
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "signature": signature,
                    }
                )

            elif node.type == "struct_specifier":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = source_bytes[
                        name_node.start_byte : name_node.end_byte
                    ].decode("utf-8")
                    symbols.append(
                        {
                            "name": name,
                            "type": "class_",
                            "line_start": node.start_point[0] + 1,
                            "line_end": node.end_point[0] + 1,
                            "signature": f"struct {name}",
                        }
                    )

            for child in node.children:
                extract_from_node(child, source_bytes)

        extract_from_node(tree.root_node, bytes(source_code, "utf-8"))
        return symbols

    except Exception as e:
        print(f"Error parsing C file {filename}: {e}")
        return []
