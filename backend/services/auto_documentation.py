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
        """
        Check if function already has documentation (double-check).
        Note: The caller usually filters by database 'has_docstring' first.
        """
        language = (language or "").lower().strip()
        
        # Normalize language names
        aliases = {
            "asm": "assembly",
            "nasm": "assembly",
            "yasm": "assembly",
            "gas": "assembly",
            "cob": "cobol",
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "c++": "cpp",
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
```
{f"Additional context: {context}" if context else ""}

Generate a concise, clear docstring that follows {language} conventions.
- For Python: Google style or Sphinx style docstring.
- For C/C++: Doxygen style (/** ... */).
- For Assembly/COBOL: Comment block above function.

Include:
1. Brief description
2. Parameters (if any)
3. Return value (if any)

Return ONLY the docstring text. Do not include markdown code blocks around it unless it's part of the syntax."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical documentation expert. Output only the raw docstring/comment block.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            content = response.choices[0].message.content
            docstring = (content or "").strip()
            
            # Cleanup: remove markdown code fences if LLM added them
            if docstring.startswith("```"):
                # Remove first line (```language)
                lines = docstring.split("\n")
                if len(lines) > 1:
                    docstring = "\n".join(lines[1:])
                if docstring.endswith("```"):
                    docstring = docstring[:-3]
            
            return docstring.strip()
        except Exception as e:
            print(f"Error generating docstring for {function_name}: {e}")
            return f"TODO: Add documentation (Auto-generation failed: {str(e)})"

    async def document_symbol(
        self, symbol: Dict, file_content: str, language: str
    ) -> Optional[Dict]:
        """
        Generate documentation for a single symbol (function/method).

        Returns:
            Dict with 'symbol_id', 'docstring', 'line_number' or None if skipped
        """
        # Ensure we are looking at a valid symbol type
        valid_types = ["function", "method", "class", "procedure"]
        symbol_type = symbol.get("type", "")
        # Handle enum value if it's an object, or string if raw
        if hasattr(symbol_type, "value"):
             symbol_type = symbol_type.value
        
        if str(symbol_type) not in valid_types:
            return None

        start_line = symbol.get("start_line", 0)
        end_line = symbol.get("end_line", 0)
        
        if start_line < 1:
            return None

        lines = file_content.splitlines()
        
        # Safety check for line numbers
        if start_line > len(lines):
            return None
            
        # Extract code snippet (context)
        # We take the function body plus a bit of context if needed
        # Adjust 0-based index vs 1-based line number
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line) if end_line else min(len(lines), start_idx + 50)
        
        # Limit context to avoid token limits
        if end_idx - start_idx > 200:
             end_idx = start_idx + 200
        
        function_code = "\n".join(lines[start_idx:end_idx])

        # Double check if it's already documented (in case DB is stale)
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
            "insert_line": start_line, 
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
            # Add file_id to symbol dict if missing, for convenience
            if "file_id" not in symbol:
                symbol["file_id"] = file_id
            
            doc = await self.document_symbol(symbol, content, language)
            if doc:
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
            max_files: Maximum number of files to process
        """
        all_documentation = []
        
        # Process files up to the limit
        files_to_process = files[:max_files]
        
        for file in files_to_process:
            if not file.get("content"):
                continue
            
            # Ensure symbols is a list
            symbols = file.get("symbols", [])
            if not symbols:
                continue
                
            docs = await self.document_file(
                file_id=file["id"],
                file_path=file["path"],
                content=file["content"],
                symbols=symbols,
                language=file.get("language", "python"),
            )
            all_documentation.extend(docs)
            
        return all_documentation
