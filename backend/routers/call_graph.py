"""
Call graph API endpoints.
"""

import re
from collections import defaultdict
from typing import Dict, List

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.call_relationship import CallRelationship
from models.file import File
from models.repository import Repository
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/call-graph", tags=["call-graph"])


def detect_cycles_dfs(graph: Dict[str, List[str]]) -> List[List[str]]:
    """
    Detect all cycles in a directed graph using DFS.
    Returns list of cycles (each cycle is a list of node names).
    """
    cycles = []
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node: str):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                cycle_start_idx = path.index(neighbor)
                cycle = path[cycle_start_idx:] + [neighbor]
                normalized_cycle = tuple(sorted(cycle))
                if normalized_cycle not in [tuple(sorted(c)) for c in cycles]:
                    cycles.append(cycle)

        path.pop()
        rec_stack.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    return cycles


def extract_imports_from_file(file_path: str, content: str, language: str) -> List[str]:
    """
    Extract import/include statements from file content.
    Returns list of imported module/file names.
    """
    imports = []

    if language == "python":
        import_patterns = [
            r"^\s*import\s+([\w\.]+)",
            r"^\s*from\s+([\w\.]+)\s+import",
        ]
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.extend(matches)

    elif language == "c":
        include_pattern = r'#include\s+["<]([\w\./]+)[">]'
        matches = re.findall(include_pattern, content)
        imports.extend(matches)

    elif language == "assembly":
        include_patterns = [
            r'%include\s+"([\w\./]+)"',
            r"\bINCLUDE\s+([\w\./]+)",
        ]
        for pattern in include_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            imports.extend(matches)

    elif language == "cobol":
        copy_pattern = r"\bCOPY\s+([\w-]+)"
        matches = re.findall(copy_pattern, content, re.IGNORECASE)
        imports.extend(matches)

    return list(set(imports))


@router.get("/repositories/{repository_id}/call-graph")
def get_call_graph(repository_id: str, db: Session = Depends(get_db)):
    """
    Get call graph for repository.
    Shows function call relationships (who calls whom).
    Reads from pre-computed call_relationships table.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Query all call relationships for this repository
    relationships = (
        db.query(CallRelationship)
        .filter(CallRelationship.repository_id == repository_id)
        .all()
    )

    if not relationships:
        return {
            "repository_id": repository_id,
            "total_functions": 0,
            "total_calls": 0,
            "nodes": [],
            "edges": [],
            "message": "No function calls detected. Make sure your repository contains analyzable code (Python, C, Assembly, or COBOL).",
        }

    nodes_map = {}

    for rel in relationships:
        if rel.caller_name and rel.caller_name not in nodes_map:
            nodes_map[rel.caller_name] = {
                "id": rel.caller_name,
                "name": rel.caller_name,
                "file": rel.caller_file,
                "line": None,
                "calls": [],
                "called_by": [],
            }
        if rel.callee_name and rel.callee_name not in nodes_map:
            nodes_map[rel.callee_name] = {
                "id": rel.callee_name,
                "name": rel.callee_name,
                "file": rel.callee_file or "external",
                "line": None,
                "is_external": rel.is_external,
                "calls": [],
                "called_by": [],
            }

    for rel in relationships:
        if rel.caller_name and rel.callee_name:
            if rel.caller_name in nodes_map:
                nodes_map[rel.caller_name]["calls"].append(rel.callee_name)
            if rel.callee_name in nodes_map:
                nodes_map[rel.callee_name]["called_by"].append(rel.caller_name)

    nodes = list(nodes_map.values())

    edges = [
        {
            "from": rel.caller_name,
            "to": rel.callee_name,
            "file": rel.caller_file,
            "line": rel.call_line,
            "is_external": rel.is_external,
        }
        for rel in relationships
        if rel.caller_name and rel.callee_name
    ]

    return {
        "repository_id": repository_id,
        "total_functions": len(nodes),
        "total_calls": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


@router.get("/repositories/{repository_id}/stats")
def get_call_graph_stats(repository_id: str, db: Session = Depends(get_db)):
    """
    Get call graph statistics for repository overview cards.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Count unique functions
    unique_functions = (
        db.query(func.count(func.distinct(CallRelationship.caller_name)))
        .filter(CallRelationship.repository_id == repository_id)
        .scalar()
    )

    # Count total function calls
    total_calls = (
        db.query(func.count(CallRelationship.id))
        .filter(CallRelationship.repository_id == repository_id)
        .scalar()
    )

    # Find dead functions
    all_functions = (
        db.query(func.distinct(CallRelationship.caller_name))
        .filter(CallRelationship.repository_id == repository_id)
        .all()
    )
    called_functions = (
        db.query(func.distinct(CallRelationship.callee_name))
        .filter(
            CallRelationship.repository_id == repository_id,
            CallRelationship.is_external == False,
        )
        .all()
    )

    all_func_set = {f[0] for f in all_functions if f[0]}
    called_func_set = {f[0] for f in called_functions if f[0]}
    dead_functions_count = len(all_func_set - called_func_set)

    # Detect circular dependencies
    relationships = (
        db.query(CallRelationship)
        .filter(
            CallRelationship.repository_id == repository_id,
            CallRelationship.is_external == False,
        )
        .all()
    )

    graph = defaultdict(list)
    for rel in relationships:
        if rel.caller_name and rel.callee_name:
            graph[rel.caller_name].append(rel.callee_name)

    cycles = detect_cycles_dfs(dict(graph))
    circular_deps_count = len(cycles)

    return {
        "repository_id": repository_id,
        "total_functions": unique_functions or 0,
        "total_calls": total_calls or 0,
        "dead_functions": dead_functions_count,
        "circular_dependencies": circular_deps_count,
    }


@router.get("/repositories/{repository_id}/dependencies")
def get_dependencies(repository_id: str, db: Session = Depends(get_db)):
    """
    Get file-level dependency graph.
    Shows which files import/include which other files.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    files = db.query(File).filter(File.repository_id == repository_id).all()

    if not files:
        return {
            "repository_id": repository_id,
            "total_files": 0,
            "total_dependencies": 0,
            "files": [],
            "dependencies": [],
        }

    file_deps = {}
    imported_by_map = defaultdict(list)
    total_deps = 0

    for file in files:
        if not file.source:
            continue

        imports = extract_imports_from_file(file.file_path, file.source, file.language)
        file_deps[file.file_path] = {
            "file": file.file_path,
            "language": file.language,
            "imports": imports,
            "imported_by": [],
        }

        for imported in imports:
            imported_by_map[imported].append(file.file_path)
            total_deps += 1

    for file_path, importers in imported_by_map.items():
        if file_path in file_deps:
            file_deps[file_path]["imported_by"] = importers

    return {
        "repository_id": repository_id,
        "total_files": len(file_deps),
        "total_dependencies": total_deps,
        "files": list(file_deps.values()),
        "dependencies": [],
    }


@router.get("/repositories/{repository_id}/dead-code")
def get_dead_code(repository_id: str, db: Session = Depends(get_db)):
    """
    Find dead code (unused functions) in repository.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    caller_stats = (
        db.query(
            CallRelationship.caller_name,
            CallRelationship.caller_file,
            func.count(CallRelationship.id).label("call_count"),
        )
        .filter(CallRelationship.repository_id == repository_id)
        .group_by(CallRelationship.caller_name, CallRelationship.caller_file)
        .all()
    )

    called_functions_names = (
        db.query(CallRelationship.callee_name)
        .filter(
            CallRelationship.repository_id == repository_id,
            CallRelationship.is_external == False,
        )
        .distinct()
        .all()
    )

    called_names = {name[0] for name in called_functions_names if name[0]}

    dead_functions = [
        {
            "name": stat.caller_name,
            "file": stat.caller_file,
            "severity": "medium",
            "calls": stat.call_count,
        }
        for stat in caller_stats
        if stat.caller_name and stat.caller_name not in called_names
    ]

    return {
        "repository_id": repository_id,
        "dead_functions": dead_functions,
        "total_dead": len(dead_functions),
    }


@router.get("/repositories/{repository_id}/circular-deps")
def get_circular_dependencies(repository_id: str, db: Session = Depends(get_db)):
    """
    Find circular dependencies in call graph using DFS cycle detection.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    relationships = (
        db.query(CallRelationship)
        .filter(
            CallRelationship.repository_id == repository_id,
            CallRelationship.is_external == False,
        )
        .all()
    )

    if not relationships:
        return {
            "repository_id": repository_id,
            "circular_dependencies": [],
            "total_cycles": 0,
        }

    graph = defaultdict(list)
    for rel in relationships:
        if rel.caller_name and rel.callee_name:
            graph[rel.caller_name].append(rel.callee_name)

    cycles = detect_cycles_dfs(dict(graph))

    circular_deps = []
    for cycle in cycles:
        cycle_length = len(cycle) - 1

        if cycle_length <= 2:
            severity = "high"
        elif cycle_length <= 4:
            severity = "medium"
        else:
            severity = "low"

        circular_deps.append(
            {
                "cycle": cycle,
                "length": cycle_length,
                "severity": severity,
            }
        )

    severity_order = {"high": 0, "medium": 1, "low": 2}
    circular_deps.sort(key=lambda x: (severity_order[x["severity"]], x["length"]))

    return {
        "repository_id": repository_id,
        "circular_dependencies": circular_deps,
        "total_cycles": len(circular_deps),
    }
