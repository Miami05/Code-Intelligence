from pathlib import Path
from typing import Dict, List, Optional

from parsers.assembly_parser import AssemblyParser
from parsers.c_parser import CParser
from parsers.cobol_parser import CobolParser
from parsers.python_parser import PythonParser


class ParseManager:
    """Manages multi-language code parsing"""

    def __init__(self):
        self.parsers = {
            ".py": PythonParser(),
            ".c": CParser(),
            ".h": CParser(),
            ".asm": AssemblyParser(),
            ".s": AssemblyParser(),
            ".S": AssemblyParser(),
            ".cbl": CobolParser(),
            ".cob": CobolParser(),
            ".cpy": CobolParser(),
        }

        self.language_map = {
            ".py": "python",
            ".c": "c",
            ".h": "c",
            ".asm": "assembly",
            ".s": "assembly",
            ".S": "assembly",
            ".cbl": "cobol",
            ".cob": "cobol",
            ".cpy": "cobol",
        }

    def get_language_from_extension(self, file_path: str) -> str:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        return self.language_map.get(ext, "unknown")

    def parse_file(self, file_path: str, repository_id: str) -> List[Dict]:
        """Parse file based on extension"""
        ext = Path(file_path).suffix.lower()
        parser = self.parsers.get(ext)
        if parser:
            try:
                return parser.parse_file(file_path, repository_id)
            except Exception as e:
                print(f"❌ Error parsing {file_path}: {e}")
                return []
        print(f"⚠️  No parser for extension: {ext}")
        return []

    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return list(self.parsers.keys())

    def supported_languages(self) -> List[str]:
        """Get list of supported file extensions"""
        return list(set(self.language_map.values()))
