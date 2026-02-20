"""
Large file handler for files with 100k+ lines.
Uses existing ParseManager with batch processing for memory efficiency.

NOTE:
- Full file is still parsed (required for AST/tree-sitter correctness).
- DB inserts are batched to reduce memory spikes during persistence.
- If ParseManager returns a huge list, peak memory is still dominated by that list.
"""

import asyncio
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List

from parsers.parser_manager import ParseManager


class StreamingParser:
    BATCH_SIZE = 1000
    LINE_THRESHOLD = 100000

    def __init__(self) -> None:
        self.parse_manager = ParseManager()

    def should_stream(self, file_path: str) -> bool:
        """Check if file exceeds the large file threshold"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for i, _ in enumerate(f, 1):
                    if i > self.LINE_THRESHOLD:
                        return True
            return False
        except OSError:
            return False

    async def parse_large_files_batched(
        self, file_path: str, repository_id: str
    ) -> AsyncIterator[List[Dict]]:
        """
        Parse large file using ParseManager (non-blocking via thread pool).
        Yields symbols in batches of BATCH_SIZE for memory-efficient DB inserts.
        """
        loop = asyncio.get_event_loop()
        all_symbols = await loop.run_in_executor(
            None, self.parse_manager.parse_file, file_path, repository_id
        )
        for i in range(0, len(all_symbols), self.BATCH_SIZE):
            batch = all_symbols[i : i + self.BATCH_SIZE]
            yield batch
            await asyncio.sleep(0)

    def get_file_stats(self, file_path: str) -> Dict:
        """Get basic stats about a large file before parsing"""
        try:
            line_count = 0
            size_bytes = Path(file_path).stat().st_size
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for _ in f:
                    line_count += 1
            return {
                "line_count": line_count,
                "size_bytes": size_bytes,
                "is_large": line_count > self.LINE_THRESHOLD,
                "language": self.parse_manager.get_language_from_extension(file_path),
            }
        except OSError:
            return {}
