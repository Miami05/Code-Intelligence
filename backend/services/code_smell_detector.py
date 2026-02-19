"""Code Smell Detection Service"""

import re
import uuid
from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict


@dataclass
class SmellFinding:
    """Represents a detected code smell"""

    file_id: uuid.UUID
    symbol_id: Optional[uuid.UUID]
    smell_type: str
    severity: str
    title: str
    description: str
    suggestion: str
    start_line: str
    end_line: str
    metric_value: Optional[int]
    metric_threshold: Optional[int]


class ClassData(TypedDict):
    symbol: dict[str, Any]
    methods: list[dict[str, Any]]


class CodeSmellDetector:
    """Detects various code smells in source code"""

    LONG_METHOD_LINES = 50
    GOD_CLASS_METHODS = 20
    GOD_CLASS_LINES = 500
    LARGE_CLASS_LINES = 300
    LONG_PARAM_LIST = 5

    def __init__(self):
        pass

    def detect_long_methods(
        self, file_id: uuid.UUID, symbols: List[Dict]
    ) -> List[SmellFinding]:
        """Detect methods/functions that are too long"""
        findings = []
        for symbol in symbols:
            if symbol.get("type") not in ["function", "method"]:
                continue
            line_count = symbol.get("end_line", 0) - symbol.get("start_line", 0)
            if line_count > self.LONG_METHOD_LINES:
                severity = (
                    "high" if line_count > self.LONG_METHOD_LINES * 2 else "medium"
                )
                findings.append(
                    SmellFinding(
                        file_id=file_id,
                        symbol_id=symbol.get("id"),
                        smell_type="long_method",
                        severity=severity,
                        title=f"Long Method: {symbol.get('name', 'unknown')}",
                        description=f"Method '{symbol.get('name')}' has {line_count} lines, exceeding the recommended maximum of {self.LONG_METHOD_LINES} lines.",
                        suggestion="Consider breaking this method into smaller, more focused methods. Apply Extract Method refactoring.",
                        start_line=symbol.get("start_line", 0),
                        end_line=symbol.get("end_line", 0),
                        metric_value=line_count,
                        metric_threshold=self.LONG_METHOD_LINES,
                    )
                )
        return findings

    def detect_god_classes(
        self, file_id: uuid.UUID, file_path: str, symbols: List[Dict], file_lines: int
    ) -> List[SmellFinding]:
        """Detect classes with too many responsibilities (God Class)"""
        findings = []

        classes: dict[str, ClassData] = {}
        for symbol in symbols:
            if symbol.get("type") == "class":
                class_id = str(symbol["id"])
                classes[class_id] = {"symbol": symbol, "methods": []}
            elif symbol.get("type") in ["method", "function"]:
                parent_id = symbol.get("parent_id")
                if parent_id and parent_id in classes:
                    classes[parent_id]["methods"].append(symbol)
        for class_id, class_data in classes.items():
            class_symbol = class_data["symbol"]
            method_count = len(class_data["methods"])
            class_lines = class_symbol.get("end_line", 0) - class_symbol.get(
                "start_line", 0
            )
            is_god_class = (
                method_count > self.GOD_CLASS_METHODS
                or class_lines > self.GOD_CLASS_LINES
            )
            if is_god_class:
                severity = (
                    "critical"
                    if (
                        method_count > self.GOD_CLASS_METHODS * 1.5
                        or class_lines > self.GOD_CLASS_LINES * 2
                    )
                    else "high"
                )
                description_parts = []
                if method_count > self.GOD_CLASS_METHODS:
                    description_parts.append(
                        f"{method_count} methods (threshold: {self.GOD_CLASS_METHODS})"
                    )
                if class_lines > self.GOD_CLASS_LINES:
                    description_parts.append(
                        f"{class_lines} lines (threshold: {self.GOD_CLASS_LINES})"
                    )
                if (
                    method_count > self.GOD_CLASS_METHODS
                    and class_lines > self.GOD_CLASS_LINES
                ):
                    metric_value = method_count
                    metric_threshold = self.GOD_CLASS_METHODS
                    metric_name = "methods"
                elif method_count > self.GOD_CLASS_METHODS:
                    metric_value = method_count
                    metric_threshold = self.GOD_CLASS_METHODS
                    metric_name = "methods"
                else:
                    metric_value = class_lines
                    metric_threshold = self.GOD_CLASS_LINES
                    metric_name = "lines"
                findings.append(
                    SmellFinding(
                        file_id=file_id,
                        symbol_id=class_symbol.get("id"),
                        smell_type="god_class",
                        severity=severity,
                        title=f"God Class: {class_symbol.get('name', 'unknown')}",
                        description=f"Class '{class_symbol.get('name')}' has too many responsibilities: {', '.join(description_parts)}.",
                        suggestion="Consider splitting this class into multiple smaller classes with single responsibilities. Apply Extract Class refactoring.",
                        start_line=class_symbol.get("start_line", 0),
                        end_line=class_symbol.get("end_line", 0),
                        metric_value=metric_value,
                        metric_threshold=metric_threshold,
                    )
                )
        return findings

    def detect_feature_envy(
        self, file_id: uuid.UUID, symbols: List[Dict], content: str
    ) -> List[SmellFinding]:
        """
        Detect Feature Envy: methods that use more data from other classes
        than from their own class.
        """
        findings = []
        for symbol in symbols:
            if symbol.get("type") not in ["method", "function"]:
                continue
            start_line = symbol.get("start_line", 0)
            end_line = symbol.get("end_line", 0)
            lines = content.split("\n")[start_line - 1 : end_line]
            method_body = "\n".join(lines)
            self_refs = len(re.findall(r"\bself\.|\bthis\.", method_body))
            external_refs = len(re.findall(r"\b\w+\.\w+", method_body)) - self_refs
            if external_refs > 5 and external_refs > self_refs * 2:
                findings.append(
                    SmellFinding(
                        file_id=file_id,
                        symbol_id=symbol.get("id"),
                        smell_type="feature_envy",
                        severity="medium",
                        title=f"Feature Envy: {symbol.get('name', 'unknown')}",
                        description=f"Method '{symbol.get('name')}' accesses external data ({external_refs} times) more than its own class data ({self_refs} times).",
                        suggestion="Consider moving this method to the class whose data it primarily uses. Apply Move Method refactoring.",
                        start_line=start_line,
                        end_line=end_line,
                        metric_value=external_refs,
                        metric_threshold=self_refs * 2,
                    )
                )
        return findings

    def scan_file(
        self, file_id: uuid.UUID, file_path: str, content: str, symbols: List[Dict]
    ) -> List[SmellFinding]:
        """Scan a single file for all code smells"""
        findings = []
        file_lines = len(content.split("\n"))
        findings.extend(self.detect_long_methods(file_id, symbols))
        findings.extend(
            self.detect_god_classes(file_id, file_path, symbols, file_lines)
        )
        findings.extend(self.detect_feature_envy(file_id, symbols, content))

        return findings

    def scan_repository(self, files: List[Dict]) -> List[SmellFinding]:
        """
        Scan entire repository for code smells.
        Args:
            files: List of dicts with keys: id, path, content, symbols
        """
        all_findings = []
        for file in files:
            if not file.get("content"):
                continue
            findings = self.scan_file(
                file_id=file["id"],
                file_path=file["path"],
                content=file["content"],
                symbols=file.get("symbols", []),
            )
            all_findings.extend(findings)
        return all_findings
