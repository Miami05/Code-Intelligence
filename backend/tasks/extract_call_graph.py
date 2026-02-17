"""
Celery task to extract call graph relationships and save to database.
Runs after repository parsing is complete.
"""

from analyzers.call_graph import CallGraphAnalyzer
from celery_app import celery_app
from database import SessionLocal
from models import File, Repository, Symbol
from models.call_relationship import CallRelationship


@celery_app.task(bind=True, name="tasks.extract_call_graph.extract_call_graph_task")
def extract_call_graph_task(self, repository_id: str):
    """
    Extract function call relationships and save to database.

    This task:
    1. Loads all files and symbols for the repository
    2. Analyzes code to find function calls
    3. Saves CallRelationship records to database

    Args:
        repository_id: UUID of the repository

    Returns:
        Dictionary with extraction statistics
    """
    db = SessionLocal()

    try:
        repo = db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            print(f"❌ Repository {repository_id} not found")
            return {"error": "Repository not found"}

        print(f"📊 Extracting call graph for: {repo.name} (ID: {repository_id})")

        # Get all files for this repository
        files = db.query(File).filter(File.repository_id == repository_id).all()

        if not files:
            print(f"⚠️  No files found for repository {repository_id}")
            return {
                "repository_id": repository_id,
                "files_analyzed": 0,
                "calls_extracted": 0,
                "status": "no_files",
            }

        # Build files_data structure for analyzer
        files_data = []

        for file in files:
            # Skip files without source code
            if not file.source:
                print(f"  ⚠️  No source code for: {file.file_path}")
                continue

            # Get symbols for this file
            symbols = db.query(Symbol).filter(Symbol.file_id == file.id).all()

            # Convert symbols to dict format
            symbols_data = [
                {
                    "id": str(sym.id),
                    "name": sym.name,
                    "type": sym.type.value,
                    "line_start": sym.line_start,
                    "line_end": sym.line_end,
                }
                for sym in symbols
            ]

            files_data.append(
                {
                    "file_path": file.file_path,
                    "language": file.language,
                    "source_code": file.source,  # Read from database instead of disk
                    "symbols": symbols_data,
                }
            )

        if not files_data:
            print(f"⚠️  No files with source code found")
            return {
                "repository_id": repository_id,
                "files_analyzed": 0,
                "calls_extracted": 0,
                "status": "no_source_code",
            }

        print(f"  📁 Loaded {len(files_data)} files with source code")

        # Initialize analyzer
        analyzer = CallGraphAnalyzer(repository_id)

        # Extract all call relationships
        all_calls = []
        for file_data in files_data:
            language = file_data["language"]
            file_path = file_data["file_path"]
            source = file_data["source_code"]
            symbols = file_data["symbols"]

            if not source:
                continue

            # Analyze based on language
            try:
                if language == "python":
                    calls = analyzer.analyze_python_file(file_path, source, symbols)
                elif language == "c":
                    calls = analyzer.analyze_c_file(file_path, source, symbols)
                elif language == "assembly":
                    calls = analyzer.analyze_assembly_file(file_path, source, symbols)
                elif language == "cobol":
                    calls = analyzer.analyze_cobol_file(file_path, source, symbols)
                else:
                    print(f"  ⚠️  Unsupported language for call graph: {language}")
                    continue

                if calls:
                    print(f"  ✓ {file_path}: {len(calls)} calls found")
                all_calls.extend(calls)
            except Exception as e:
                print(f"  ⚠️  Error analyzing {file_path}: {e}")
                continue

        saved_count = 0
        for call in all_calls:
            try:
                call_record = CallRelationship(
                    repository_id=repository_id,
                    caller_symbol_id=call.get("caller_symbol_id"),
                    caller_name=call["caller_name"],
                    caller_file=call["caller_file"],
                    callee_name=call["callee_name"],
                    callee_file=call.get("callee_file"),
                    callee_symbol_id=call.get("callee_symbol_id"),
                    call_line=call["call_line"],  # FIXED: Use call_line not caller_line
                    is_external=call["is_external"],
                )
                db.add(call_record)
                saved_count += 1
            except Exception as e:
                print(f"  ⚠️  Error saving call: {e}")
                continue

        db.commit()

        print(f"✅ Call graph extraction complete for {repository_id}")
        print(f"   Files analyzed: {len(files_data)}")
        print(f"   Calls extracted: {saved_count}")

        return {
            "repository_id": repository_id,
            "files_analyzed": len(files_data),
            "calls_extracted": saved_count,
            "status": "completed",
        }

    except Exception as e:
        print(f"❌ Error extracting call graph: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
        raise

    finally:
        db.close()
