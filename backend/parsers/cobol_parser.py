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
            print("✅ Tree-sitter COBOL parser loaded")
        except Exception as e:
            print(f"⚠️  Tree-sitter COBOL parser not available ({e}), using regex-based parsing")
            self.parser = None
            self.language = None

    def parse_file(self, file_path: str, repository_id: str) -> List[Dict]:
        """Extract symbols from COBOL file"""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source_code = f.read()
        
        # Always try both methods and combine results
        symbols = []
        
        if self.parser:
            try:
                ts_symbols = self._parse_with_tree_sitter(
                    file_path, source_code.encode(), repository_id
                )
                symbols.extend(ts_symbols)
                print(f"🌳 Tree-sitter found {len(ts_symbols)} symbols in {os.path.basename(file_path)}")
            except Exception as e:
                print(f"⚠️  Tree-sitter failed for {file_path}: {e}")
        
        # Fallback to regex if tree-sitter found nothing
        if not symbols:
            regex_symbols = self._parse_with_regex(file_path, source_code, repository_id)
            symbols.extend(regex_symbols)
            print(f"🔍 Regex found {len(regex_symbols)} symbols in {os.path.basename(file_path)}")
        
        return symbols

    def _parse_with_regex(
        self, file_path: str, source_code: str, repository_id: str
    ) -> List[Dict]:
        """Fallback regex-based parsing for COBOL"""
        symbols = []
        lines = source_code.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper().strip()
            
            # Skip empty lines and comments
            if not line_upper or line_upper.startswith("*"):
                continue
            
            # Extract PROGRAM-ID
            program_match = re.match(r"PROGRAM-ID\.\s+([A-Z0-9\-]+)", line_upper)
            if program_match:
                name = program_match.group(1)
                symbols.append(
                    {
                        "name": name,
                        "type": "program",
                        "signature": f"PROGRAM-ID. {name}",
                        "file_path": file_path,
                        "line_start": line_num,
                        "line_end": line_num,
                        "repository_id": repository_id,
                    }
                )
                continue
            
            # Extract SECTION
            section_match = re.match(r"^([A-Z][A-Z0-9\-]*)\s+SECTION\.", line_upper)
            if section_match:
                name = section_match.group(1)
                symbols.append(
                    {
                        "name": name,
                        "type": "procedure",
                        "signature": f"{name} SECTION.",
                        "file_path": file_path,
                        "line_start": line_num,
                        "line_end": line_num,
                        "repository_id": repository_id,
                    }
                )
                continue
            
            # Extract PARAGRAPH (must end with a period and be standalone)
            paragraph_match = re.match(r"^([A-Z0-9][A-Z0-9\-]*)\.\s*$", line_upper)
            if paragraph_match:
                name = paragraph_match.group(1)
                # Exclude division/section names
                if name not in [
                    "IDENTIFICATION",
                    "ENVIRONMENT",
                    "DATA",
                    "PROCEDURE",
                    "WORKING-STORAGE",
                    "LINKAGE",
                    "FILE",
                    "SCREEN",
                    "INPUT-OUTPUT",
                    "FILE-CONTROL",
                    "CONFIGURATION",
                ]:
                    symbols.append(
                        {
                            "name": name,
                            "type": "procedure",
                            "signature": f"{name}.",
                            "file_path": file_path,
                            "line_start": line_num,
                            "line_end": line_num,
                            "repository_id": repository_id,
                        }
                    )
                    continue
            
            # Extract 01-level data items (important variables)
            data_match = re.match(
                r"^\s*(01)\s+([A-Z0-9][A-Z0-9\-]+)",
                line_upper,
            )
            if data_match:
                level = data_match.group(1)
                name = data_match.group(2)
                symbols.append(
                    {
                        "name": name,
                        "type": "variable",
                        "signature": line.strip(),
                        "file_path": file_path,
                        "line_start": line_num,
                        "line_end": line_num,
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
        
        # Extract program_id
        if node.type == "program_id":
            name_node = node.named_children[0] if node.named_children else None
            if name_node:
                name = source_code[name_node.start_byte : name_node.end_byte].decode(
                    "utf-8"
                ).strip()
                symbols.append(
                    {
                        "name": name,
                        "type": "program",
                        "signature": f"PROGRAM-ID. {name}",
                        "file_path": file_path,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "repository_id": repository_id,
                    }
                )
        
        # Extract paragraphs
        elif node.type == "paragraph":
            for child in node.children:
                if child.type == "paragraph_name":
                    name = source_code[child.start_byte : child.end_byte].decode(
                        "utf-8"
                    ).strip()
                    symbols.append(
                        {
                            "name": name,
                            "type": "procedure",
                            "signature": f"{name}.",
                            "file_path": file_path,
                            "line_start": node.start_point[0] + 1,
                            "line_end": node.end_point[0] + 1,
                            "repository_id": repository_id,
                        }
                    )
                    break
        
        # Extract sections
        elif node.type == "section":
            for child in node.children:
                if child.type == "section_name":
                    name = source_code[child.start_byte : child.end_byte].decode(
                        "utf-8"
                    ).strip()
                    symbols.append(
                        {
                            "name": name,
                            "type": "procedure",
                            "signature": f"{name} SECTION.",
                            "file_path": file_path,
                            "line_start": node.start_point[0] + 1,
                            "line_end": node.end_point[0] + 1,
                            "repository_id": repository_id,
                        }
                    )
                    break
        
        # Extract data declarations (01 level)
        elif node.type == "data_description":
            level_node = None
            name_node = None
            for child in node.children:
                if child.type == "level_number" and child.text and child.text.decode("utf-8").strip() == "01":
                    level_node = child
                elif child.type in ["data_name", "identifier"]:
                    name_node = child
            
            if level_node and name_node:
                name = source_code[name_node.start_byte : name_node.end_byte].decode(
                    "utf-8"
                ).strip()
                symbols.append(
                    {
                        "name": name,
                        "type": "variable",
                        "signature": source_code[node.start_byte : node.end_byte].decode("utf-8").strip()[:100],
                        "file_path": file_path,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "repository_id": repository_id,
                    }
                )
        
        # Recurse through all children
        for child in node.children:
            self._extract_symbols(child, source_code, file_path, repository_id, symbols)


def extract_cobol_symbols(source_code: str, filename: str) -> List[Dict]:
    """
    Wrapper function to extract COBOL symbols.
    Compatible with generic parser interface.
    """
    parser = CobolParser()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".cob", delete=False) as f:
        f.write(source_code)
        temp_path = f.name

    try:
        symbols = parser.parse_file(temp_path, "temp")
        return symbols
    finally:
        os.unlink(temp_path)
