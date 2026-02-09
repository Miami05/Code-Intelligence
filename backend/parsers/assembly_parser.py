import os
import re
import tempfile
import uuid
from typing import Dict, List

from tree_sitter_languages import get_language, get_parser


class AssemblyParser:
    """Parser for x86/x64 Assembly (supports multiple syntaxes)"""

    def __init__(self):
        try:
            self.parser = get_parser("asm")
            self.language = get_language("asm")
        except:
            print(
                "⚠️  Tree-sitter assembly parser not available, using regex-based parsing"
            )
            self.parser = None
            self.language = None

    def parse_files(self, file_path: str, repository_id: str) -> List[Dict]:
        """Extract symbols from Assembly file"""
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
        """Fallback regex-based parsing for Assembly"""
        symbols = []
        lines = source_code.split("\n")
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            label_match = re.match(
                r"^([._a-zA-Z][._a-zA-Z0-9]*):(?!\s*;)", line_stripped
            )
            if label_match:
                label_name = label_match.group(1)
                if not label_name.startswith("L"):
                    symbols.append(
                        {
                            "symbol_id": str(uuid.uuid4()),
                            "name": label_name,
                            "type": "function",
                            "signature": f"{label_name}:",
                            "file_path": file_path,
                            "start_line": line_num,
                            "end_line": line_num,
                            "repository_id": repository_id,
                        }
                    )
            section_match = re.match(
                r"^\.(text|data|bss|rodata)(?:\s|$)", line_stripped
            )
            if section_match:
                section_name = section_match.group(1)
                symbols.append(
                    {
                        "symbol_id": str(uuid.uuid4()),
                        "name": f"{section_name}",
                        "type": "section",
                        "signature": f".{section_name}",
                        "file_path": file_path,
                        "start_line": line_num,
                        "end_line": line_num,
                        "repository_id": repository_id,
                    }
                )
            global_match = re.match(
                r"^\.(globl|global)\s+([._a-zA-Z][._a-zA-Z0-9]*)", line_stripped
            )
            if global_match:
                symbol_name = global_match.group(2)
                symbols.append(
                    {
                        "symbol_id": str(uuid.uuid4()),
                        "name": symbol_name,
                        "type": "global",
                        "signature": f".global {symbol_name}",
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
        """Recursively extract Assembly symbols using tree-sitter"""
        if node.type == "label":
            name = (
                source_code[node.start_byte : node.end_byte].decode("utf-8").strip(":")
            )
            symbols.append(
                {
                    "symbol_id": str(uuid.uuid4()),
                    "name": name,
                    "type": "function",
                    "signature": f"{name}",
                    "file_path": file_path,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                    "repository_id": repository_id,
                }
            )
        for child in node.children:
            self._extract_symbols(child, source_code, file_path, repository_id, symbols)


def extract_assembly_symbols(source_code: str, filename: str) -> List[Dict]:
    """
    Wrapper function to extract Assembly symbols.
    Compatible with parse_repository.py interface.
    """
    parser = AssemblyParser()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".asm", delete=False) as f:
        f.write(source_code)
        temp_path = f.name
        try:
            symbols = parser.parse_files(temp_path, "temp")
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
