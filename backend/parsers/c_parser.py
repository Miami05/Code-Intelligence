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
            elif node.type == "struct_specfifier":
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = source_code[
                        name_node.start_byte : name_node.end_byte
                    ].decode("utf-8")
                    symbols.append(
                        {
                            "symbol_id": str(uuid.uuid4()),
                            "name": name,
                            "type": "struct",
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
                    name = source_code[
                        name_node.start_byte : name_node.end_byte
                    ].decode("utf-8")
                    symbols.append(
                        {
                            "symbol_id": str(uuid.uuid4()),
                            "name": name,
                            "type": "enum",
                            "signature": f"enum {name}",
                            "file_path": file_path,
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1,
                            "repository_id": repository_id,
                        }
                    )
                elif node.type == "type_definition":
                    for child in reversed(node.children):
                        name = source_code[child.start_byte : child.end_byte].decode(
                            "utf-8"
                        )
                        signature = source_code[node.start_byte : node.end_byte].decode(
                            "utf-8", errors="ignore"
                        )
                        symbols.append(
                            {
                                "symbols_id": str(uuid.uuid4()),
                                "name": name,
                                "type": "typedef",
                                "signature": signature.strip(),
                                "file_path": file_path,
                                "start_line": node.start_point[0] + 1,
                                "end_line": node.end_point[0] + 1,
                                "repository_id": repository_id,
                            }
                        )
                        break
                    for child in node.children:
                        self._extract_symbols(
                            child, source_code, file_path, repository_id, symbols
                        )

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
