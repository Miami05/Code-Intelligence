"""
Large file handler for 100k+ line files.
Batches DB inserts to avoid memory spikes.
Uses the same parser functions as parse_repository.py.
"""

import os
from typing import Dict, Generator, List

from parsers.assembly_parser import extract_assembly_symbols
from parsers.c_parser import extract_c_symbols
from parsers.cobol_parser import extract_cobol_symbols
from parsers.python_parser import extract_python_symbols

LANGUAGE_CONFIG = {
    "python": {".py": extract_python_symbols},
    "c": {".c": extract_c_symbols, ".h": extract_c_symbols},
    "assembly": {
        ".asm": extract_assembly_symbols,
        ".s": extract_assembly_symbols,
        ".S": extract_assembly_symbols,
    },
    "cobol": {
        ".cob": extract_cobol_symbols,
        ".cbl": extract_cobol_symbols,
        ".COB": extract_cobol_symbols,
        ".CBL": extract_cobol_symbols,
    },
}

EXTENSION_MAP = {}
for lang, ext_map in LANGUAGE_CONFIG.items():
    for ext, func in ext_map.items():
        EXTENSION_MAP[ext] = (lang, func)

LINE_THRESHOLD = 100_000
BATCH_SIZE = 1_000


class StreamingParser:
    """Handles large file parsing with batched symbol yielding."""

    def should_stream(self, file_path: str) -> bool:
        """Return True if file has more than LINE_THRESHOLD lines."""
        try:
            count = 0
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for _ in f:
                    count += 1
                    if count > LINE_THRESHOLD:
                        return True
            return False
        except Exception:
            return False

    def get_parser_for_file(self, file_path: str):
        """Return (language, parser_func) for a given file path, or None."""
        ext = os.path.splitext(file_path)[1]
        return EXTENSION_MAP.get(ext)

    def parse_in_batches(
        self, file_path: str, repository_id: str
    ) -> Generator[List[Dict], None, None]:
        """
        Parse a large file and yield symbols in batches of BATCH_SIZE.
        Uses the same parser functions as parse_repository.py.
        """
        parser_info = self.get_parser_for_file(file_path)
        if not parser_info:
            print(f"⚠️  No parser found for: {file_path}")
            return

        language, parser_func = parser_info

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
            symbols = parser_func(source, file_path)
            for i in range(0, len(symbols), BATCH_SIZE):
                yield symbols[i : i + BATCH_SIZE]

        except Exception as e:
            print(f"❌ StreamingParser error on {file_path}: {e}")
            return

    def get_file_stats(self, file_path: str) -> Dict:
        """Return basic stats about a file."""
        try:
            line_count = 0
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for _ in f:
                    line_count += 1
            size_bytes = os.path.getsize(file_path)
            ext = os.path.splitext(file_path)[1]
            parser_info = EXTENSION_MAP.get(ext)
            return {
                "line_count": line_count,
                "size_bytes": size_bytes,
                "is_large": line_count > LINE_THRESHOLD,
                "language": parser_info[0] if parser_info else "unknown",
            }
        except Exception:
            return {}
