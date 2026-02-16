"""
Call graph API endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from analyzers import call_graph
from analyzers.call_graph import CallGraphAnalyzer
from analyzers.dead_code import DeadCodeAnalyzer
from analyzers.dependency_analyzer import DependencyAnalyzer
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
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    files = db.query(File).filter(File.repository_id == repository_id).all()
    files_data = []
    for file in files:
        symbols = db.query(Symbol).filter(Symbol.file_id == file.id).all()
        try:
            with open(f"/tmp/code_intel_{repository_id}/{file.file_path}", "r") as f:
                source_code = f.read()
        except:
            source_code = ""
        files_data.append(
            {
                "file_path": file.file_path,
                "language": file.language,
                "source_code": source_code,
                "symbols": [
                    {
                        "id": sym.id,
                        "name": sym.name,
                        "type": sym.type,
                        "line_start": sym.line_start,
                        "line_end": sym.line_end,
                    }
                    for sym in symbols
                ],
            }
        )
    analyzer = CallGraphAnalyzer(repository_id)
    call_graph = analyzer.build_call_graph(files_data)
    return call_graph


@router.get("/repositories/{repository_id}/dependencies")
def get_dependecies(repository_id: str, db: Session = Depends(get_db)):
    """
    Get file-level dependency graph.
    Shows which files import/include which other files.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    files = db.query(File).filter(File.repository_id == repository_id).all()
    files_data = []
    for file in files:
        try:
            with open(f"/tmp/code_intel_{repository_id}/{file.file_path}", "r") as f:
                source_code = f.read()
        except:
            source_code = ""
        files_data.append(
            {
                "file_path": file.file_path,
                "language": file.language,
                "source_code": source_code,
            }
        )
    analyzer = DependencyAnalyzer(repository_id)
    dep_graph = analyzer.build_dependency_graph(files_data)
    return dep_graph


@router.get("/repositories/{repository_id}/dead-code")
def get_dead_code(repository_id: str, db: Session = Depends(get_db)):
    """
    Find dead code (unused functions) in repository.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    files = db.query(File).filter(File.repository_id == repository_id).all()
    files_data = []
    for file in files_data:
        symbols = db.query(Symbol).filter(Symbol.file_id == file.id).all()
        try:
            with open(f"/tmp/code_intel_{repository_id}/{file.file_path}", "r") as f:
                source_code = f.read()
        except:
            source_code = ""
        files_data.append(
            {
                "file_path": file.file_path,
                "language": file.language,
                "source_code": source_code,
                "symbols": [
                    {
                        "id": sym.id,
                        "name": sym.name,
                        "type": sym.type.value,
                        "line_start": sym.line_start,
                        "line_end": sym.line_end,
                    }
                    for sym in symbols
                ],
            }
        )
    graph_analyzer = CallGraphAnalyzer(repository_id)
    call_graph = graph_analyzer.build_call_graph(files_data)
    dead_analyzer = DeadCodeAnalyzer(repository_id)
    dead_functions = dead_analyzer.find_dead_functions(call_graph)
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
    files = db.query(File).filter(File.repository_id == repository_id).all()
    files_data = []
    for file in files:
        symbols = db.query(Symbol).filter(Symbol.file_id == file.id).all()
        try:
            with open(f"/tmp/code_intel_{repository_id}/{file.file_path}", "r") as f:
                source_code = f.read()
        except:
            source_code = ""
        files_data.append(
            {
                "file_path": file.file_path,
                "language": file.language,
                "source_code": source_code,
                "symbols": [
                    {
                        "id": sym.id,
                        "name": sym.name,
                        "type": sym.type.value,
                        "line_start": sym.line_start,
                        "line_end": sym.line_end,
                    }
                    for sym in symbols
                ],
            }
        )
    graph_analyzer = CallGraphAnalyzer(repository_id)
    call_graph = graph_analyzer.build_call_graph(files_data)
    dead_analyzer = DeadCodeAnalyzer(repository_id)
    circular_deps = dead_analyzer.find_circular_dependencies(call_graph)
    return {
        "repository_id": repository_id,
        "circular_dependencies": circular_deps,
        "total_cycles": len(circular_deps),
    }
