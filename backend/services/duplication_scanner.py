"""Code Duplication Detection using MinHash and Token-based Analysis"""

import hashlib
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Set


@dataclass
class CodeBlock:
    """Represents a block of code for duplication analysis"""

    file_id: uuid.UUID
    file_path: str
    start_line: int
    end_line: int
    content: str
    tokens: List[str]
    hash_signature: str
    line_count: int


class MinHashSignature:
    """MinHash algorithm for approximate similarity detection"""

    def __init__(self, num_hashes: int = 128):
        self.num_hashes = num_hashes
        self.hash_functions = [
            lambda x, seed=i: int(hashlib.md5(f"{seed}{x}".encode()).hexdigest(), 16)
            for i in range(num_hashes)
        ]

    def compute_signature(self, tokens: Set[str]) -> List[int]:
        """Compute MinHash signature for a set of tokens"""
        if not tokens:
            return [0] * self.num_hashes
        signature = []
        for hash_func in self.hash_functions:
            min_hash = min(hash_func(token) for token in tokens)
            signature.append(min_hash)
        return signature

    def similarity(self, sig1: List[int], sig2: List[int]) -> float:
        """Calculate Jaccard similarity between two signatures"""
        if len(sig1) != len(sig2):
            return 0.0
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)


class DuplicateScanner:
    """Detects code duplications using MinHash and token-based analysis"""

    def __init__(
        self,
        min_block_size: int = 6,
        similarity_threshold: float = 0.8,
        min_tokens: int = 50,
    ):
        self.min_block_size = min_block_size
        self.similarity_threshold = similarity_threshold
        self.min_tokens = min_tokens
        self.minhash = MinHashSignature(num_hashes=128)

    def tokenize_code(self, code: str, language: str = "python") -> List[str]:
        """
        Tokenize code into meaningful tokens.
        Removes comments, whitespace, and normalizes identifiers.
        """
        language = language.lower()
        if language == "python":
            code = re.sub(r"#.*?$", "", code, flags=re.MULTILINE)
            code = re.sub(r'""".*?"""|\'\'\'.*?\'\'\'', "", code, flags=re.DOTALL)
        elif language in ["c", "cpp", "c++"]:
            code = re.sub(r"//.*?$", "", code, flags=re.MULTILINE)
            code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        elif language in ["assembly", "asm", "x86", "arm"]:
            code = re.sub(r";.*?$", "", code, flags=re.MULTILINE)
            code = re.sub(r"//.*?$", "", code, flags=re.MULTILINE)
            code = re.sub(r"#.*?$", "", code, flags=re.MULTILINE)
        elif language == "cobol":
            code = re.sub(r"^\s*\*.*?$", "", code, flags=re.MULTILINE)
            code = re.sub(r"\*>.*?$", "", code, flags=re.MULTILINE)
        tokens = self._extract_tokens(code, language)
        tokens = [t.lower() for t in tokens if len(t) > 1]
        return tokens

    def _extract_tokens(self, code: str, language: str) -> List[str]:
        """Extract tokens based on language syntax"""
        if language == "python":
            tokens = re.findall(
                r"\b\w+\b|[+\-*/%=<>!&|^~]|[\[\]{}();,.]", code, re.MULTILINE
            )
        elif language in ["c", "cpp", "c++"]:
            tokens = re.findall(
                r"#\w+|"
                r"\b\w+\b|"
                r"[+\-*/%=<>!&|^~]|"
                r"[\[\]{}();,.]|"
                r"->|\.\.\.",
                code,
                re.MULTILINE,
            )
        elif language in ["assembly", "asm", "x86", "arm"]:
            tokens = re.findall(
                r"\b[a-zA-Z_]\w*\b|" r"0x[0-9a-fA-F]+|" r"\b\d+\b|" r"[\[\](),+\-*]",
                code,
                re.MULTILINE,
            )
        elif language == "cobol":
            tokens = re.findall(
                r"\b[A-Z0-9\-]+\b|" r"\d+|" r"[().,;]",
                code,
                re.MULTILINE,
            )
            cobol_noise = {
                "DIVISION",
                "SECTION",
                "PROCEDURE",
                "DATA",
                "WORKING-STORAGE",
                "FILE",
                "IDENTIFICATION",
                "ENVIRONMENT",
                "CONFIGURATION",
            }
            tokens = [t for t in tokens if t.upper() not in cobol_noise]

        else:
            tokens = re.findall(
                r"\b\w+\b|[+\-*/%=<>!&|^~]|[\[\]{}();,.]", code, re.MULTILINE
            )
        return tokens

    def create_code_blocks(
        self, file_id: uuid.UUID, file_path: str, content: str, language: str = "python"
    ) -> List[CodeBlock]:
        """
        Split file into overlapping code blocks for analysis.
        Uses sliding window approach.
        """
        lines = content.split("\n")
        blocks = []
        min_block = self._get_min_block_size(language)
        step_size = max(1, min_block // 2)
        for i in range(0, len(lines) - min_block + 1, step_size):
            end_idx = min(i + min_block, len(lines))
            block_lines = lines[i:end_idx]
            block_content = "\n".join(block_lines)
            if not block_content.strip():
                continue
            tokens = self.tokenize_code(block_content, language)
            if len(tokens) < self.min_tokens:
                continue
            token_set = set(tokens)
            signature = self.minhash.compute_signature(token_set)
            hash_sig = hashlib.md5(str(signature).encode()).hexdigest()
            block = CodeBlock(
                file_id=file_id,
                file_path=file_path,
                start_line=i + 1,
                end_line=end_idx,
                content=block_content,
                tokens=tokens,
                hash_signature=hash_sig,
                line_count=len(block_lines),
            )
            blocks.append(block)
        return blocks

    def _get_min_block_size(self, language: str) -> int:
        """Language-specific minimum block sizes"""
        language = language.lower()
        if language == "cobol":
            return 10
        elif language in ["assembly", "asm", "x86", "arm"]:
            return 8
        else:
            return self.min_block_size

    def find_duplicate(self, all_blocks: List[CodeBlock]) -> List[Dict]:
        """
        Find duplicate code blocks across all files.
        Returns list of duplication pairs with similarity scores.
        """
        duplicates = []
        hash_buckets = defaultdict(list)
        for block in all_blocks:
            bucket_key = block.hash_signature[:8]
            hash_buckets[bucket_key].append(block)
        compared_pairs = set()
        for block1 in all_blocks:
            bucket_key = block1.hash_signature[:8]
            candidates = hash_buckets.get(bucket_key, [])
            for block2 in candidates:
                if block1.file_id == block2.file_id:
                    continue
                pair_key = tuple(
                    sorted(
                        {
                            (str(block1.file_id), block1.start_line),
                            (str(block2.file_id), block2.start_line),
                        }
                    )
                )
                if pair_key in compared_pairs:
                    continue
                compared_pairs.add(pair_key)
                sig1 = self.minhash.compute_signature(set(block1.content))
                sig2 = self.minhash.compute_signature(set(block2.content))
                similarity = self.minhash.similarity(sig1, sig2)
                if similarity >= self.similarity_threshold:
                    duplicates.append(
                        {
                            "file1_id": block1.file_id,
                            "file1_path": block1.file_path,
                            "file1_start_line": block1.start_line,
                            "file1_end_line": block1.end_line,
                            "file2_id": block2.file_id,
                            "file2_path": block2.file_path,
                            "file2_start_line": block2.start_line,
                            "file2_end_line": block2.end_line,
                            "similarity_score": similarity,
                            "duplicate_lines": min(
                                block1.line_count, block2.line_count
                            ),
                            "duplicate_tokens": min(
                                len(block1.tokens), len(block2.tokens)
                            ),
                            "code_snippet": block1.content[:500],
                            "hash_signature": block1.hash_signature,
                        }
                    )
        duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)
        return duplicates

    def scan_repository(self, files: List[Dict[str, Any]]) -> List[Dict]:
        """
        Scan entire repository for duplications.
        Args:
            files: List of dicts with keys: id, path, content, language
        Returns:
            List of duplication findings
        """
        all_blocks = []
        for file in files:
            if not file.get("content"):
                continue
            language = file.get("language") or self._detect_language(file["path"])
            blocks = self.create_code_blocks(
                file_id=file["id"],
                file_path=file["path"],
                content=file["content"],
                language=language,
            )
            all_blocks.extend(blocks)
        duplicates = self.find_duplicate(all_blocks)
        return duplicates

    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension"""
        ext = file_path.lower().split(".")[-1]
        language_map = {
            "py": "python",
            "c": "c",
            "h": "c",
            "cpp": "cpp",
            "cc": "cpp",
            "cxx": "cpp",
            "hpp": "cpp",
            "asm": "assembly",
            "s": "assembly",
            "cob": "cobol",
            "cbl": "cobol",
            "cpy": "cobol",
        }
        return language_map.get(ext, "python")
