import os
import re
import tempfile
import uuid
from typing import Dict, List

from tree_sitter_languages import get_language, get_parser


class CobolParser:
    """Parser for COBOL language"""

    def __init__(self):
        try:
            self.parser = get_parser("cobol")
            self.language = get_language("cobol")
        except:
            print(
                "⚠️  Tree-sitter COBOL parser not available, using regex-based parsing"
            )
            self.parser = None
            self.language = None

    def parse_file(self, file_path: str, repository_id: str) -> List[Dict]:
        """Extract symbols from COBOL file"""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source_code = f.read()
        if self.parser:
            return self._parse_with_tree_sitter(
                file_path, source_code.encode(), repository_id
            )
        else:
            return self._parse_with_regex(file_path, source_code, repository_id)

    def _parse_with_regex(
        self, file_path: str, source_code: str, repository_id: str
    ) -> List[Dict]:
        """Fallback regex-based parsing for COBOL"""
        symbols = []
        lines = source_code.split("\n")
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper().strip()
            program_match = re.match(r"PROGRAM-ID\.\s+([A-Z0-9\-]+)", line_upper)
            if program_match:
                name = program_match.group(1)
                symbols.append(
                    {
                        "symbol_id": str(uuid.uuid4()),
                        "name": name,
                        "type": "program",
                        "signature": f"PROGRAM-ID. {name}",
                        "file_path": file_path,
                        "start_line": line_num,
                        "end_line": line_num,
                        "repository_id": repository_id,
                    }
                )
            paragraph_match = re.match(r"^([A-Z0-9\-]+)\.\s*$", line_upper)
            if paragraph_match:
                name = paragraph_match.group(1)
                if name not in [
                    "IDENTIFICATION",
                    "ENVIRONMENT",
                    "DATA",
                    "PROCEDURE",
                    "WORKING-STORAGE",
                    "LINKAGE",
                    "FILE",
                    "SCREEN",
                ]:
                    symbols.append(
                        {
                            "symbol_id": str(uuid.uuid4()),
                            "name": name,
                            "type": "paragraph",
                            "signature": f"{name}.",
                            "file_path": file_path,
                            "start_line": line_num,
                            "end_line": line_num,
                            "repository_id": repository_id,
                        }
                    )
            data_match = re.match(
                r"^\s*(01|02|03|04|05|06|07|08|09|10|[1-4][0-9])\s+([A-Z0-9\-]+)",
                line_upper,
            )
            if data_match:
                level = data_match.group(1)
                name = data_match.group(2)
                if level == "01":
                    symbols.append(
                        {
                            "symbol_id": str(uuid.uuid4()),
                            "name": name,
                            "type": "variable",
                            "signature": line.strip(),
                            "file_path": file_path,
                            "start_line": line_num,
                            "end_line": line_num,
                            "repository_id": repository_id,
                        }
                    )
        return symbols

    def _parse_with_tree_sitter(
        self, file_path: str, source_code: bytes, repository_id: str
    ) -> List[Dict]:
        """Tree-sitter based parsing (when available)"""
        if self.parser is None:
            return []
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
        """Recursively extract COBOL symbols using tree-sitter"""
        if node.type == "program_id":
            name_node = node.named_children[0] if node.named_children else None
            if name_node:
                name = source_code[name_node.start_byte : name_node.end_byte].decode(
                    "utf-8"
                )
                symbols.append(
                    {
                        "symbols": str(uuid.uuid4()),
                        "name": name,
                        "type": "program",
                        "signature": f"PROGRAM-ID. {name}",
                        "file_path": file_path,
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "repository_id": repository_id,
                    }
                )
            elif node.type == "paragraph":
                for child in node.children:
                    if child.type == "paragraph_name":
                        name = source_code[child.start_byte : child.end_byte].decode(
                            "utf-8"
                        )
                        symbols.append(
                            {
                                "symbol_id": str(uuid.uuid4()),
                                "name": name,
                                "type": "paragraph",
                                "signature": f"{name}.",
                                "file_path": file_path,
                                "start_line": node.start_point[0] + 1,
                                "end_line": node.end_point[0] + 1,
                                "repository_id": repository_id,
                            }
                        )
                        break
        for child in node.children:
            self._extract_symbols(child, source_code, file_path, repository_id, symbols)


def extract_cobol_symbols(source_code: str, filename: str) -> List[Dict]:
    """
    Wrapper function to extract COBOL symbols.
    Compatible with parse_repository.py interface.
    """
    parser = CobolParser()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".cob", delete=False) as f:
        f.write(source_code)
        temp_path = f.name
    try:
        symbols = parser.parse_file(temp_path, "temp")
        result = []
        for sym in symbols:
            result.append(
                {
                    "name": sym["name"],
                    "type": sym["type"],
                    "line_start": sym["start_line"],
                    "line_end": sym["end_line"],
                    "signature": sym.get("signature", ""),
                }
            )
        return result
    finally:
        os.unlink(temp_path)
