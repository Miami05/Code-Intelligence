"""
Call graph API endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models.call_relationship import CallRelationship
from models.file import File
from models.repository import Repository
from models.symbol import Symbol

router = APIRouter(prefix="/api/call-graph", tags=["call-graph"])


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

    # Build nodes (unique functions)
    nodes_map = {}
    
    # First pass: Create nodes
    for rel in relationships:
        # Add caller node
        if rel.caller_name and rel.caller_name not in nodes_map:
            nodes_map[rel.caller_name] = {
                "id": rel.caller_name,
                "name": rel.caller_name,
                "file": rel.caller_file,
                "line": None,
                "calls": [],      # Initialize empty list
                "called_by": [],  # Initialize empty list
            }
        # Add callee node
        if rel.callee_name and rel.callee_name not in nodes_map:
            nodes_map[rel.callee_name] = {
                "id": rel.callee_name,
                "name": rel.callee_name,
                "file": rel.callee_file or "external",
                "line": None,
                "is_external": rel.is_external,
                "calls": [],      # Initialize empty list
                "called_by": [],  # Initialize empty list
            }

    # Second pass: Populate relationships (calls/called_by)
    for rel in relationships:
        if rel.caller_name and rel.callee_name:
            # Caller calls Callee
            if rel.caller_name in nodes_map:
                nodes_map[rel.caller_name]["calls"].append(rel.callee_name)
            
            # Callee is called by Caller
            if rel.callee_name in nodes_map:
                nodes_map[rel.callee_name]["called_by"].append(rel.caller_name)

    nodes = list(nodes_map.values())

    # Build edges (call relationships)
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

    # Count unique functions (distinct caller names)
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

    # Find dead functions (functions that are never called as callee)
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

    # TODO: Implement circular dependency detection
    circular_deps_count = 0

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

    # TODO: Implement file dependency extraction
    return {
        "repository_id": repository_id,
        "total_files": 0,
        "total_dependencies": 0,
        "files": [],
        "dependencies": [],
        "message": "File dependency extraction not yet implemented",
    }


@router.get("/repositories/{repository_id}/dead-code")
def get_dead_code(repository_id: str, db: Session = Depends(get_db)):
    """
    Find dead code (unused functions) in repository.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Get all functions that call something
    all_functions = (
        db.query(CallRelationship.caller_name, CallRelationship.caller_file)
        .filter(CallRelationship.repository_id == repository_id)
        .distinct()
        .all()
    )

    # Get all functions that are called
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

    # Dead functions are those that exist but are never called
    dead_functions = [
        {"name": func[0], "file": func[1]}
        for func in all_functions
        if func[0] and func[0] not in called_names
    ]

    return {
        "repository_id": repository_id,
        "dead_functions": dead_functions,
        "total_dead": len(dead_functions),
    }


@router.get("/repositories/{repository_id}/circular-deps")
def get_circular_dependencies(repository_id: str, db: Session = Depends(get_db)):
    """
    Find circular dependencies in call graph.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # TODO: Implement circular dependency detection using DFS
    return {
        "repository_id": repository_id,
        "circular_dependencies": [],
        "total_cycles": 0,
        "message": "Circular dependency detection coming soon",
    }
