"""
Cyclomatic complexity and maintainability index calculator.
Supports Python, C, COBOL, Assembly.

Notes:
- Complexity is a fast text-based heuristic (regex), not a full parser.
- We return a breakdown so you can explain *why* a score is high.
- We avoid accidental overcounting for Python comprehensions.
"""

import math
import re
from typing import Any, Dict, Tuple


def calculate_cyclomatic_complexity(source_code: str, language: str) -> int:
    """Returns only the complexity number (backwards compatible)."""
    complexity, _ = calculate_cyclomatic_complexity_with_breakdown(
        source_code, language
    )
    return complexity


def calculate_cyclomatic_complexity_with_breakdown(
    source_code: str, language: str
) -> Tuple[int, Dict[str, int]]:
    """
    Returns:
        (complexity, breakdown)
    """
    lang = (language or "").strip().lower()

    if lang == "python":
        return _complexity_python(source_code)
    if lang == "c":
        return _complexity_c(source_code)
    if lang == "cobol":
        return _complexity_cobol(source_code)
    if lang == "assembly":
        return _complexity_assembly(source_code)

    return 1, {"base": 1}


def _complexity_python(code: str) -> Tuple[int, Dict[str, int]]:
    """
    Count Python decision points (text-based heuristic).

    We count:
      - if/elif/for/while/except/case
      - boolean operators and/or (adds extra paths)
    We also detect comprehensions with "for ... if ..." inside [], (), {} as *breakdown only*.
    (We don't add extra complexity for comprehensions to avoid double-counting.)
    """
    complexity = 1
    breakdowns: Dict[str, int] = {"base": 1}
    patterns: Dict[str, str] = {
        "if": r"\bif\b",
        "elif": r"\belif\b",
        "for": r"\bfor\b",
        "while": r"\bwhile\b",
        "except": r"\bexcept\b",
        "case": r"\bcase\b",
        "and": r"\band\b",
        "or": r"\bor\b",
    }
    for name, pattern in patterns.items():
        count = len(re.findall(pattern, code))
        breakdowns[name] = count
        complexity += count
    comp = len(re.findall(r"[\[\(\{][^\n]*\bfor\b[^\n]*\bif\b[^\n]*[\]\)\}]", code))
    breakdowns["comprehensions_for_if"] = comp
    return max(1, complexity), breakdowns


def _complexity_c(code: str) -> Tuple[int, Dict[str, int]]:
    """Count C decision points (text-based heuristic)."""
    complexity = 1
    breakdowns: Dict[str, int] = {"base": 1}
    patterns: Dict[str, str] = {
        "if": r"\bif\b",
        "for": r"\bfor\b",
        "while": r"\bwhile\b",
        "do": r"\bdo\b",
        "case": r"\bcase\b",
        "ternary_?": r"\?",
        "logical_and_&&": r"\&\&",
        "logical_or_||": r"\|\|",
    }
    for name, pattern in patterns.items():
        count = len(re.findall(pattern, code))
        breakdowns[name] = count
        complexity += count
    return max(1, complexity), breakdowns


def _complexity_cobol(code: str) -> Tuple[int, Dict[str, int]]:
    """Count COBOL decision points (text-based heuristic)."""
    complexity = 1
    breakdowns: Dict[str, int] = {"base": 1}
    code_upper = code.upper()
    patterns: Dict[str, str] = {
        "IF": r"\bIF\b",
        "EVALUATE": r"\bEVALUATE\b",
        "PERFORM_UNTIL": r"\bPERFORM\s+UNTIL\b",
        "AND": r"\bAND\b",
        "OR": r"\bOR\b",
    }
    for name, pattern in patterns:
        count = len(re.findall(pattern, code_upper))
        breakdowns[name] = count
        complexity += count
    return max(1, complexity), breakdowns


def _complexity_assembly(code: str) -> Tuple[int, Dict[str, int]]:
    """Count Assembly decision points (jumps/branches) (text-based heuristic)."""
    complexity = 1
    breakdowns: Dict[str, int] = {"base": 1}
    code_upper = code.upper()
    patterns: Dict[str, str] = {
        "Jxx": r"\bJ[A-Z]+\b",
        "CALL": r"\bCALL\b",
        "RET": r"\bRET\b",
        "LOOP": r"\bLOOP\b",
    }
    for name, pattern in patterns.items():
        count = len(re.findall(pattern, code_upper))
        breakdowns[name] = count
        complexity += count
    return max(1, complexity), breakdowns


def calculate_maintainability_index(
    complexity: int, lines_of_code: int, comment_lines: int
) -> float:
    """
    Calculate Maintainability Index (0-100).
    Simplified MI inspired by Microsoft's formula.

    Higher is better.
    """
    if lines_of_code <= 0:
        return 100.0
    volume = lines_of_code * math.log(max(lines_of_code, 2))
    mi = 171.0
    mi -= 5.2 * math.log(max(volume, 1))
    mi -= 0.23 * max(complexity, 1)
    mi -= 16.2 * math.log(max(lines_of_code, 1))
    comment_ratio = (comment_lines / lines_of_code) if lines_of_code > 0 else 0.0
    mi += 50.0 * comment_ratio
    mi = max(0.0, min(100.0, mi))
    return round(mi, 2)


def count_lines_and_comments(source_code: str, language: str) -> Tuple[int, int]:
    """
    Count lines of code and comment lines.

    Returns:
        (lines_of_code, comment_lines)
    """
    lang = (language or "").strip().lower()
    lines = source_code.split("\n")
    code_lines = 0
    comment_lines = 0
    if lang == "python":
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if '"""' in stripped or "'''" in stripped:
                comment_lines += 1
                if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                    continue
                in_docstring = not in_docstring
                continue
            if in_docstring or stripped.startswith("#"):
                comment_lines += 1
            else:
                code_lines += 1
    elif lang == "c":
        in_block_comment = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if "/*" in stripped:
                in_block_comment = True
            if in_block_comment:
                comment_lines += 1
                if "/*" in stripped:
                    in_block_comment = False
                continue
            if stripped.startswith("//"):
                comment_lines += 1
            else:
                code_lines += 1
    elif lang == "cobol":
        for line in lines:
            if len(line) > 6:
                if line[6] == "*":
                    comment_lines += 1
                elif line.strip():
                    code_lines += 1
                else:
                    if line.strip():
                        code_lines += 1
    elif lang == "assembly":
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(";") or stripped.startswith("#"):
                comment_lines += 1
            else:
                code_lines += 1
    else:
        code_lines = len([l for l in lines if l.strip()])
        comment_lines = 0
    return code_lines, comment_lines


def analyze_code_quality(source_code: str, language: str) -> Dict[str, Any]:
    """
    Full code quality analysis.

    Returns:
        {
            "cyclomatic_complexity": int,
            "complexity_breakdown": {str: int},
            "maintainability_index": float,
            "lines_of_code": int,
            "comment_lines": int,
            "quality_rating": str
        }
    """
    complexity, breakdown = calculate_cyclomatic_complexity_with_breakdown(
        source_code, language
    )
    loc, comments = count_lines_and_comments(source_code, language)
    mi = calculate_maintainability_index(complexity, loc, comments)
    if mi >= 85:
        rating = "excellent"
    elif mi >= 65:
        rating = "good"
    elif mi >= 50:
        rating = "fair"
    else:
        rating = "poor"

    return {
        "cyclomatic_complexity": complexity,
        "complexity_breakdown": breakdown,
        "maintainability_index": mi,
        "lines_of_code": loc,
        "comment_lines": comments,
        "quality_rating": rating,
    }
