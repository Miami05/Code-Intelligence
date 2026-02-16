"""
Dependency analyzer - file-level dependencies.
Supports: Python, C, Assembly, COBOL
"""

import re
from typing import Dict, List, Set


class DependencyAnalyzer:
    """
    Analyzes file-level dependencies (imports, includes).
    Supports: Python, C, Assembly, COBOL
    """

    def __init__(self, repository_id: str):
        self.repository_id = repository_id

    def analyze_python_imports(self, file_path: str, source_code: str) -> List[str]:
        """
        Extract Python imports.

        Matches:
        - import module
        - from module import x
        - from package.module import x
        """
        imports = []
        import_pattern = re.compile(
            r"^\s*(?:from\s+([a-zA-Z0-9_.]+)\s+)?import\s+([a-zA-Z0-9_, ]+)",
            re.MULTILINE,
        )
        for match in import_pattern.finditer(source_code):
            module = match.group(1) or match.group(2).split(",")[0].strip()
            imports.append(module)
        return list(set(imports))

    def analyze_c_includes(self, file_path: str, source_code: str) -> List[str]:
        """
        Extract C includes.

        Matches:
        - #include "file.h"
        - #include <file.h>
        """
        includes = []
        include_pattern = re.compile(r'#include\s+[<"]([^>"]+)[>"]')
        for match in include_pattern.finditer(source_code):
            header = match.group(1)
            includes.append(header)
        return list(set(includes))

    def analyze_assembly_includes(self, file_path: str, source_code: str) -> List[str]:
        """
        Extract Assembly include directives.

        Supports various syntaxes:
        - .include "file.inc"      (GAS - GNU Assembler)
        - %include "file.asm"      (NASM)
        - .import file             (Some assemblers)
        - include file.inc         (MASM)
        """
        includes = []
        patterns = [
            re.compile(r'\.include\s+["\']([^"\']+)["\']', re.IGNORECASE),
            re.compile(r'%include\s+["\']([^"\']+)["\']', re.IGNORECASE),
            re.compile(r"\.import\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE),
            re.compile(
                r"^\s*include\s+([a-zA-Z0-9_./]+)", re.IGNORECASE | re.MULTILINE
            ),
            re.compile(r"\.extern\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE),
            re.compile(r"\.global\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE),
        ]
        for pattern in patterns:
            for match in pattern.finditer(source_code):
                include_file = match.group(1)
                includes.append(include_file)
        return list(set(includes))

    def analyze_cobol_copies(self, file_path: str, source_code: str) -> List[str]:
        """
        Extract COBOL COPY statements (similar to includes).

        Matches:
        - COPY COPYBOOK.
        - COPY "filename.cpy".
        - COPY filename IN library.
        - COPY filename REPLACING ...
        """
        copies = []
        patterns = [
            re.compile(r'\bCOPY\s+["\']([^"\']+)["\']', re.IGNORECASE),
            re.compile(r"\bCOPY\s+([A-Z0-9\-_]+)\.", re.IGNORECASE),
            re.compile(r"\bCOPY\s+([A-Z0-9\-_]+)\s+IN\s+", re.IGNORECASE),
            re.compile(r"\bCOPY\s+([A-Z0-9\-_]+)\s+REPLACING", re.IGNORECASE),
        ]
        for pattern in patterns:
            for match in pattern.finditer(source_code):
                copybook = match.group(1)
                if copybook not in ["REPLACING", "SUPPRESS"]:
                    copies.append(copybook)
        return list(set(copies))

    def build_dependency_graph(self, files_data: List[Dict]) -> Dict:
        """
        Build file-level dependency graph.

        Args:
            files_data: List of {file_path, language, source_code}

        Returns:
            Dependency graph with files as nodes
        """
        dependencies = {}
        for file_data in files_data:
            file_path = file_data["file_path"]
            language = file_data["language"]
            source = file_data["source_code"]
            if language == "python":
                deps = self.analyze_python_imports(file_path, source)
            elif language == "c":
                deps = self.analyze_c_includes(file_path, source)
            elif language == "assembly":
                deps = self.analyze_assembly_includes(file_path, source)
            elif language == "cobol":
                deps = self.analyze_cobol_copies(file_path, source)
            else:
                deps = []
            dependencies[file_path] = {
                "file": file_path,
                "language": language,
                "imports": deps,
                "imported_by": [],
            }
        for file_path, data in dependencies.items():
            for imported in data["imports"]:
                if data["language"] == "python":
                    imported_guess = imported.replace(".", "/") + ".py"
                else:
                    imported_guess = imported
                for other_file, other_data in dependencies.items():
                    if other_file.endswith(imported_guess) or other_file.endswith(
                        imported
                    ):
                        if file_path not in other_data["imported_by"]:
                            other_data["imported_by"].append(file_path)

        return {
            "files": list(dependencies.values()),
            "total_files": len(dependencies),
            "total_dependencies": sum(len(d["imports"]) for d in dependencies.values()),
            "repository_id": self.repository_id,
        }
