import traceback
import uuid
from pathlib import Path
from typing import Optional, Union

from database import SessionLocal
from models.embedding import Embedding
from models.file import File
from models.repository import Repository
from models.symbol import Symbol, SymbolType
from parsers.parser_manager import ParseManager
from utils.embeddings import generate_embedding


class CodeIngestion:
    def __init__(self):
        self.parser_manager = ParseManager()

    def ingest_repository(
        self, repo_path: Union[str, Path], repo_name: Optional[str] = None
    ):
        """Ingest multi-language code from repository"""
        repo_path = Path(repo_path)
        repo_name = repo_name or repo_path.name
        print("\n🚀 Starting multi-language ingestion")
        print(f"📂 Repository: {repo_name}")
        print(f"📍 Path: {repo_path}")
        db = SessionLocal()
        try:
            repository = (
                db.query(Repository).filter(Repository.name == repo_name).first()
            )
            if not repository:
                repository = Repository(id=uuid.uuid4(), name=repo_name)
                db.add(repository)
                db.flush()
                print("✅ Created new repository")
            else:
                print("✅ Using existing repository")
            print(f"🆔 Repository ID: {repository.id}")
            supported_exts = self.parser_manager.supported_extensions()
            all_files = []
            for ext in supported_exts:
                files = list(repo_path.rglob(f"*{ext}"))
                all_files.extend(files)
            print(f"\n📄 Found {len(all_files)} files")
            print(
                f"🔧 Supported languages: {','.join(self.parser_manager.supported_languages())}"
            )
            total_symbols = 0
            files_by_language = {}
            for file_path in all_files:
                try:
                    language = self.parser_manager.get_language_from_extension(
                        str(file_path)
                    )
                    try:
                        relative_path = str(file_path.relative_to(repo_path))
                    except ValueError:
                        relative_path = str(file_path)
                    file_record = (
                        db.query(File)
                        .filter(
                            File.repository_id == repository.id,
                            File.file_path == relative_path,
                        )
                        .first()
                    )
                    if not file_record:
                        file_record = File(
                            id=uuid.uuid4(),
                            repository=repository.id,
                            file_path=relative_path,
                            language=language,
                        )
                        db.add(file_record)
                        db.flush()
                    symbols = self.parser_manager.parse_file(
                        str(file_path), str(repository.id)
                    )
                    if not symbols:
                        continue
                    if language not in files_by_language:
                        files_by_language[language] = {"files": 0, "symbols": 0}
                    files_by_language[language]["files"] += 1
                    files_by_language[language]["symbols"] += 1
                    for symbol_dict in symbols:
                        type_mapping = {
                            "function": SymbolType.function,
                            "class_": SymbolType.class_,
                            "class": SymbolType.class_,
                            "variable": SymbolType.variable,
                            "procedure": SymbolType.procedure,
                            "label": SymbolType.label,
                            "method": SymbolType.function,
                            "struct": SymbolType.class_,
                            "enum": SymbolType.class_,
                            "typedef": SymbolType.class_,
                            "section": SymbolType.label,
                            "global": SymbolType.variable,
                            "paragraph": SymbolType.function,
                            "program": SymbolType.function,
                        }
                        symbol_type = type_mapping.get(
                            symbol_dict["type"], SymbolType.function
                        )
                        symbol = Symbol(
                            id=uuid.uuid4(),
                            file_id=file_record.id,
                            name=symbol_dict["name"],
                            type=symbol_type,
                            line_start=symbol_dict.get("start_line", 1),
                            line_end=symbol_dict.get("end_line", 1),
                            signature=symbol_dict.get("signature", ""),
                        )
                        db.add(symbol)
                        db.flush()
                        try:
                            embedding_vector = generate_embedding(
                                symbol_dict["signature"]
                            )
                            embedding = Embedding(
                                id=uuid.uuid4(),
                                symbol_id=symbol.id,
                                embedding=embedding_vector,
                            )
                            db.add(embedding)
                        except Exception as e:
                            print(
                                f"⚠️  Failed to generate embedding for {symbol.name}: {e}"
                            )
                        total_symbols += 1
                        db.commit()
                        print(
                            f"✅ {file_path.name:30} ({language:10}) → {len(symbols)} symbols"
                        )
                except Exception as e:
                    print(f"❌ Error processing {file_path.name}: {e}")
                    traceback.print_exc()
                    db.rollback()
            print(f"\n{'=' * 60}")
            print("📊 Ingestion Summary")
            print(f"{'=' * 60}")
            for lang, stats in files_by_language.items():
                print(
                    f"  {lang:12} | {stats['files']:3} files | {stats['symbols']:4} symbols"
                )
            print(f"{'=' * 60}")
            print(
                f"  TOTAL        | {len(all_files):3} files | {total_symbols:4} symbols"
            )
            print(f"{'=' * 60}\n")
            return repository.id
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            traceback.print_exc()
            db.rollback()
            raise
        finally:
            db.close()
