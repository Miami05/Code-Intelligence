"""Docstring extraction utilities for Sprint 9 auto-documentation

Supports:
- Python: AST-based docstring extraction from functions/classes
- C: JavaDoc-style /** ... */ comment blocks
- Assembly: Comment blocks (; or //) above symbols
- COBOL: Comment lines (*) above procedures
"""

import ast
from typing import Optional, Tuple


def extract_python_docstring(
    source_code: str, line_start: int
) -> Tuple[Optional[str], int]:
    """
    Extract Python docstring from source code at given line.

    Args:
        source_code: Full source code
        line_start: Starting line number of function/class

    Returns:
        Tuple of (docstring_text, docstring_length) or (None, 0)
    """
    try:
        tree = ast.parse(source_code)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if node.lineno == line_start:
                    docstring = ast.get_docstring(node)
                    if docstring:
                        clean_doc = docstring.strip()
                        return clean_doc, len(clean_doc)

        return None, 0
    except (SyntaxError, ValueError):
        return None, 0


def extract_c_docstring(source_code: str, line_start: int) -> Tuple[Optional[str], int]:
    """
    Extract C/C++ JavaDoc-style comment /** ... */ before function.

    Args:
        source_code: Full source code
        line_start: Starting line number of function

    Returns:
        Tuple of (docstring_text, docstring_length) or (None, 0)
    """
    lines = source_code.splitlines()
    if line_start <= 0 or line_start > len(lines):
        return None, 0
    doc_lines = []
    in_doc_block = False
    start_search = max(0, line_start - 10)
    for i in range(line_start - 1, start_search - 1, -1):
        line = lines[i].strip()
        if line.endswith("*/"):
            in_doc_block = True
            line = line[:-2].strip()
            if line.startswith("*"):
                line = line[1:].strip()
            if line:
                doc_lines.insert(0, line)
            continue
        if in_doc_block:
            if line.startswith("/**"):
                line = line[3:].strip()
                if line:
                    doc_lines.insert(0, line)
                break
            elif line.startswith("*"):
                line = line[1:].strip()
                if line:
                    doc_lines.insert(0, line)
            elif not line:
                continue
            else:
                break

    if doc_lines:
        docstring = " ".join(doc_lines).strip()
        return docstring, len(docstring)

    return None, 0


def extract_assembly_docstring(
    source_code: str, line_start: int
) -> Tuple[Optional[str], int]:
    """
    Extract Assembly comment block (; or //) before symbol/label.

    Args:
        source_code: Full source code
        line_start: Starting line number of symbol

    Returns:
        Tuple of (docstring_text, docstring_length) or (None, 0)
    """
    lines = source_code.splitlines()
    if line_start <= 0 or line_start > len(lines):
        return None, 0

    doc_lines = []

    for i in range(line_start - 1, -1, -1):
        line = lines[i].strip()
        if line.startswith(";"):
            comment = line[1:].strip()
            if comment:
                doc_lines.insert(0, comment)
        elif line.startswith("//"):
            comment = line[2:].strip()
            if comment:
                doc_lines.insert(0, comment)
        elif not line:
            break
        else:
            break

    if doc_lines:
        docstring = " ".join(doc_lines).strip()
        return docstring, len(docstring)

    return None, 0


def extract_cobol_docstring(
    source_code: str, line_start: int
) -> Tuple[Optional[str], int]:
    """
    Extract COBOL comment block (* in column 7) before procedure/section.

    Args:
        source_code: Full source code
        line_start: Starting line number of procedure

    Returns:
        Tuple of (docstring_text, docstring_length) or (None, 0)
    """
    lines = source_code.splitlines()
    if line_start <= 0 or line_start > len(lines):
        return None, 0

    doc_lines = []

    for i in range(line_start - 1, -1, -1):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("*"):
            comment = stripped[1:].strip()
            if comment.startswith(">"):
                comment = comment[1:].strip()
            if comment:
                doc_lines.insert(0, comment)
        elif not stripped:
            break
        else:
            break

    if doc_lines:
        docstring = " ".join(doc_lines).strip()
        return docstring, len(docstring)

    return None, 0


def extract_docstring(
    source_code: str, language: str, line_start: int
) -> Tuple[Optional[str], int]:
    """
    Universal docstring extractor that delegates to language-specific handlers.

    Args:
        source_code: Full source code
        language: Language name (python, c, assembly, cobol)
        line_start: Starting line number of symbol

    Returns:
        Tuple of (docstring_text, docstring_length) or (None, 0)
    """
    language = language.lower()

    if language == "python":
        return extract_python_docstring(source_code, line_start)
    elif language in ["c", "cpp", "c++"]:
        return extract_c_docstring(source_code, line_start)
    elif language in ["assembly", "asm"]:
        return extract_assembly_docstring(source_code, line_start)
    elif language == "cobol":
        return extract_cobol_docstring(source_code, line_start)
    else:
        return None, 0
