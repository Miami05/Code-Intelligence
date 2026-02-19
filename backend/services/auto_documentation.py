"""Auto-Documentation Service - Generate docstrings using AI"""

import re
import uuid
from typing import Dict, List, Optional

from config import settings
from openai import AsyncOpenAI


class AutoDocumentationService:
    """Generates documentation for undocumented functions using AI"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"

    def is_documented(self, function_code: str, language: str) -> bool:
        """Check if function already has documentation"""
        language = (language or "").lower().strip()
        aliases = {
            "asm": "assembly",
            "nasm": "assembly",
            "yasm": "assembly",
            "gas": "assembly",
            "cob": "cobol",
        }
        language = aliases.get(language, language)
        if language == "python":
            return bool(
                re.search(r'""".*?"""|\'\'\'.*?\'\'\'', function_code, re.DOTALL)
            )
        elif language in ["javascript", "typescript", "java", "c", "cpp", "go"]:
            return bool(re.search(r"/\*\*.*?\*/", function_code, re.DOTALL))
        elif language == "cobol":
            return bool(re.search(r"(?m)^\s*\*>|(?m)^.{6}\*", function_code))
        elif language == "assembly":
            return bool(re.search(r"(?m)^\s*[;#]", function_code))
        return False

    async def generate_docstring(
        self,
        function_name: str,
        function_code: str,
        language: str,
        context: Optional[str] = None,
    ) -> str:
        """Generate docstring for a function using AI"""
        prompt = f"""Generate documentation for the following {language} function.

Function name: {function_name}

Code:
```{language}
{function_code}
{"Additional context: " + context if context else ""}

Generate a concise, clear docstring that follows {language} conventions:

Brief description of what the function does

Parameters (with types if applicable)

Return value

Any exceptions/errors it might raise

Return ONLY the docstring text, properly formatted for {language}."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical documentation expert.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            content = response.choices[0].message.content
            docstring = (content or "").strip()
            return docstring
        except Exception as e:
            return f"# TODO: Add documentation\n# Error generating docs: {str(e)}"


async def document_symbol(
    self, symbol: Dict, file_content: str, language: str
) -> Optional[Dict]:
    """
    Generate documentation for a single symbol (function/method).

    Returns:
        Dict with 'symbol_id', 'docstring', 'line_number' or None if already documented
    """
    if symbol.get("type") not in ["function", "method"]:
        return None
    start_line = symbol.get("start_line", 0)
    end_line = symbol.get("end_line", 0)
    lines = file_content.split("\n")
    if start_line < 1 or end_line < start_line:
        return None
    function_code = "\n".join(lines[start_line - 1 : end_line])
    if self.is_documented(function_code, language):
        return None
    docstring = await self.generate_docstring(
        function_name=symbol.get("name", "unknown"),
        function_code=function_code,
        language=language,
    )
    return {
        "symbol_id": symbol.get("id"),
        "symbol_name": symbol.get("name"),
        "docstring": docstring,
        "insert_line": start_line + 1,
        "file_id": symbol.get("file_id"),
    }


async def document_file(
    self,
    file_id: uuid.UUID,
    file_path: str,
    content: str,
    symbols: List[Dict],
    language: str,
) -> List[Dict]:
    """Generate documentation for all undocumented functions in a file"""
    documentation = []
    for symbol in symbols:
        doc = await self.document_symbol(symbol, content, language)
        if doc:
            doc["file_id"] = file_id
            doc["file_path"] = file_path
            documentation.append(doc)
    return documentation


async def document_repository(
    self, files: List[Dict], max_files: int = 10
) -> List[Dict]:
    """
    Generate documentation for undocumented functions in repository.

    Args:
        files: List of dicts with keys: id, path, content, symbols, language
        max_files: Maximum number of files to process (to avoid excessive API calls)
    """
    all_documentation = []
    files_to_process = files[:max_files]
    for file in files_to_process:
        if not file.get("content"):
            continue
        docs = await self.document_file(
            file_id=file["id"],
            file_path=file["path"],
            content=file["content"],
            symbols=file.get("symbols", []),
            language=file.get("language", "python"),
        )
        all_documentation.extend(docs)
    return all_documentation
