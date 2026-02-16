"""
Call graph analyzer - extracts function call relationships.
Supports: Python, C, Assembly, COBOL
"""

import ast
import re
from typing import Dict, List, Optional


class CallGraphAnalyzer:
    """
    Analyzes code to extract function call relationships.
    Supports: Python, C, Assembly, COBOL
    """

    def __init__(self, repository_id: str):
        self.repository_id = repository_id
        self.call_relationships = []

    def analyze_python_file(
        self, file_path: str, source_code: str, symbols: List[Dict]
    ) -> List[Dict]:
        """
        Extract function calls from Python code using AST.

        Args:
            file_path: Path to the file
            source_code: Python source code
            symbols: List of functions/classes in this file

        Returns:
            List of call relationships
        """
        calls = []
        try:
            tree = ast.parse(source_code)
            function_map = {
                sym["name"]: sym for sym in symbols if sym["type"] == "function"
            }
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    caller_name = node.name
                    caller_symbol = function_map.get(caller_name)
                    if not caller_symbol:
                        continue
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            callee_name = self._extract_call_name(child)
                            if callee_name and callee_name != caller_name:
                                calls.append(
                                    {
                                        "caller_name": caller_name,
                                        "caller_file": file_path,
                                        "caller_symbol_id": caller_symbol.get("id"),
                                        "callee_name": callee_name,
                                        "callee_file": (
                                            file_path
                                            if callee_name in function_map
                                            else None
                                        ),
                                        "callee_symbol_id": (
                                            function_map[callee_name].get("id")
                                            if callee_name in function_map
                                            else None
                                        ),
                                        "call_line": child.lineno,
                                        "is_external": callee_name not in function_map,
                                    }
                                )

        except SyntaxError as e:
            print(f"⚠️  Syntax error parsing {file_path}: {e}")
        return calls

    def _extract_call_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract function name from Call node."""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None

    def analyze_c_file(
        self, file_path: str, source_code: str, symbols: List[Dict]
    ) -> List[Dict]:
        """
        Extract function calls from C code using regex.

        Args:
            file_path: Path to the file
            source_code: C source code
            symbols: List of functions in this file

        Returns:
            List of call relationships
        """
        calls = []
        function_map = {
            sym["name"]: sym for sym in symbols if sym["type"] == "function"
        }
        call_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")
        lines = source_code.split("\n")
        for symbol in symbols:
            if symbol["type"] != "function":
                continue
            caller_name = symbol["name"]
            start_line = symbol.get("line_start", 1)
            end_line = symbol.get("line_end", len(lines))
            function_body = "\n".join(lines[start_line - 1 : end_line])
            for line_offset, line in enumerate(function_body.split("\n")):
                if "//" in line:
                    line = line[: line.index("//")]
                if "*/" in line or "*/" in line:
                    continue
                for match in call_pattern.finditer(line):
                    callee_name = match.group(1)
                    if callee_name in [
                        "if",
                        "while",
                        "for",
                        "switch",
                        "return",
                        "sizeof",
                    ]:
                        continue
                    if callee_name != caller_name:
                        calls.append(
                            {
                                "caller_name": caller_name,
                                "caller_file": file_path,
                                "caller_symbol_id": symbol.get("id"),
                                "callee_name": callee_name,
                                "callee_file": (
                                    file_path if callee_name in function_map else None
                                ),
                                "callee_symbol_id": (
                                    function_map[callee_name].get("id")
                                    if callee_name in function_map
                                    else None
                                ),
                                "call_line": start_line + line_offset,
                                "is_external": callee_name not in function_map,
                            }
                        )

        return calls

    def analyze_assembly_file(
        self, file_path: str, source_code: str, symbols: List[Dict]
    ) -> List[Dict]:
        """
        Extract function/procedure calls from Assembly code.

        Supports:
        - call instruction (x86)
        - jsr instruction (68k, 6502)
        - bl instruction (ARM)
        - jal instruction (MIPS)

        Args:
            file_path: Path to the file
            source_code: Assembly source code
            symbols: List of labels/procedures in this file

        Returns:
            List of call relationships
        """
        calls = []
        function_map = {sym["name"]: sym for sym in symbols}
        call_patterns = [
            re.compile(
                r"\b(?:call|jsr|bl|jal)\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE
            ),
            re.compile(r"\bcallq?\s+\*%([a-z]+)", re.IGNORECASE),
        ]
        lines = source_code.split("\n")
        current_function = None
        for line_num, line in enumerate(lines, 1):
            if ";" in line:
                line = line[: line.index(";")]
            if "#" in line:
                line = line[: line.index("#")]
            line = line.strip()
            label_match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:", line)
            if label_match:
                label_name = label_match.group(1)
                if label_name in function_map:
                    current_function = label_name
                continue
            if current_function:
                for pattern in call_patterns:
                    for match in pattern.finditer(line):
                        callee_name = match.group(1)
                        if callee_name in [
                            "rax",
                            "rbx",
                            "rcx",
                            "rdx",
                            "rsi",
                            "rdi",
                            "eax",
                            "ebx",
                        ]:
                            continue
                        if callee_name != current_function:
                            calls.append(
                                {
                                    "caller_name": current_function,
                                    "caller_file": file_path,
                                    "caller_symbol_id": function_map[
                                        current_function
                                    ].get("id"),
                                    "callee_name": callee_name,
                                    "callee_file": (
                                        file_path
                                        if callee_name in function_map
                                        else None
                                    ),
                                    "callee_symbol_id": (
                                        function_map[callee_name].get("id")
                                        if callee_name in function_map
                                        else None
                                    ),
                                    "call_line": line_num,
                                    "is_external": callee_name not in function_map,
                                }
                            )

        return calls

    def analyze_cobol_file(
        self, file_path: str, source_code: str, symbols: List[Dict]
    ) -> List[Dict]:
        """
        Extract PERFORM and CALL statements from COBOL code.

        COBOL calls:
        - PERFORM paragraph-name
        - PERFORM section-name
        - CALL 'program-name'

        Args:
            file_path: Path to the file
            source_code: COBOL source code
            symbols: List of paragraphs/sections in this file

        Returns:
            List of call relationships
        """
        calls = []
        function_map = {sym["name"]: sym for sym in symbols}
        source_upper = source_code.upper()
        lines = source_upper.split("\n")
        perform_pattern = re.compile(r"\bPERFORM\s+([A-Z0-9\-_]+)", re.IGNORECASE)
        call_pattern = re.compile(r'\bCALL\s+[\'"]([A-Z0-9\-_]+)[\'"]', re.IGNORECASE)
        current_paragraph = None
        for line_num, line in enumerate(lines, 1):
            if len(line) > 6 and line[6] == "*":
                continue
            paragraph_match = re.match(r"\s{0,11}([A-Z0-9\-_]+)\s*\.", line)
            if paragraph_match:
                para_name = paragraph_match.group(1)
                if para_name and function_map or len(para_name) > 3:
                    current_paragraph = para_name
                continue
            if current_paragraph:
                for match in perform_pattern.finditer(line):
                    callee_name = match.group(1).strip()
                    if callee_name in ["VARYING", "UNTIL", "TIMES", "THRU", "THROUGH"]:
                        continue
                    if callee_name != current_paragraph:
                        actual_callee = None
                        for sym_name in function_map.keys():
                            if sym_name.upper() == callee_name:
                                actual_callee = sym_name
                                break
                        calls.append(
                            {
                                "caller_name": current_paragraph,
                                "caller_file": file_path,
                                "caller_symbol_id": function_map.get(
                                    current_paragraph, {}
                                ).get("id"),
                                "callee_name": actual_callee or callee_name,
                                "callee_file": file_path if actual_callee else None,
                                "callee_symbol_id": (
                                    function_map.get(actual_callee, {}).get("id")
                                    if actual_callee
                                    else None
                                ),
                                "call_line": line_num,
                                "is_external": actual_callee is None,
                            }
                        )
            for match in call_pattern.finditer(line):
                program_name = match.group(1)
                calls.append(
                    {
                        "caller_name": current_paragraph,
                        "caller_file": file_path,
                        "caller_symbol_id": function_map.get(current_paragraph, {}).get(
                            "id"
                        ),
                        "callee_name": program_name,
                        "callee_file": None,
                        "callee_symbol_id": None,
                        "call_line": line_num,
                        "is_external": True,
                    }
                )

        return calls

    def build_call_graph(self, files_data: List[Dict]) -> Dict:
        """
        Build complete call graph for repository.

        Args:
            files_data: List of {file_path, language, source_code, symbols}

        Returns:
            Call graph structure with nodes and edges
        """
        all_calls = []
        for file_data in files_data:
            language = file_data["language"]
            file_path = file_data["file_path"]
            source = file_data["source_code"]  # FIXED: was file_path["source_code"]
            symbols = file_data["symbols"]      # FIXED: was file_path["symbols"]
            if language == "python":
                calls = self.analyze_python_file(file_path, source, symbols)
            elif language == "c":
                calls = self.analyze_c_file(file_path, source, symbols)
            elif language == "assembly":
                calls = self.analyze_assembly_file(file_path, source, symbols)
            elif language == "cobol":
                calls = self.analyze_cobol_file(file_path, source, symbols)
            else:
                print(f"⚠️  Unsupported language for call graph: {language}")
                continue
            all_calls.extend(calls)
        nodes = {}
        edges = []
        for call in all_calls:
            caller = call["caller_name"]
            callee = call["callee_name"]
            if caller not in nodes:
                nodes[caller] = {
                    "name": caller,
                    "file": call["caller_file"],
                    "symbol_id": call["caller_symbol_id"],
                    "calls": [],
                    "called_by": [],
                    "is_external": False,
                }
            if callee not in nodes:
                nodes[callee] = {
                    "name": callee,
                    "file": call.get("callee_file"),
                    "symbol_id": call.get("callee_symbol_id"),
                    "calls": [],
                    "called_by": [],
                    "is_external": call["is_external"],
                }
            if callee not in nodes[caller]["calls"]:
                nodes[caller]["calls"].append(callee)
            if caller not in nodes[callee]["called_by"]:
                nodes[callee]["called_by"].append(caller)
            edges.append(
                {
                    "from": caller,
                    "to": callee,
                    "file": call["caller_file"],
                    "line": call["call_line"],
                }
            )
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "total_functions": len(nodes),
            "total_calls": len(edges),
            "repository_id": self.repository_id,
        }
