"""
Sprint 12: AI Code Completion & Assistant
Provides explain, translate, refactor, generate, and autocomplete features.
"""

import json
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel

from config import settings

router = APIRouter(prefix="/api/ai", tags=["ai-assistant"])

client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


class ExplainRequest(BaseModel):
    code: str
    language: str
    context: Optional[str] = None


class ExplainResponse(BaseModel):
    explanation: str
    complexity: str
    suggestions: List[str]


class TranslateRequest(BaseModel):
    code: str
    from_language: str
    to_language: str
    preserve_comments: bool = True


class TranslateResponse(BaseModel):
    translated_code: str
    notes: List[str]


class RefactorRequest(BaseModel):
    code: str
    language: str
    focus: str = "readibility"


class RefactorResponse(BaseModel):
    refactored_code: str
    changes: List[str]
    rationale: str


class GenerateRequest(BaseModel):
    prompt: str
    language: str
    style: str = "clean"


class GenerateResponse(BaseModel):
    code: str
    explanation: str


class AutocompleteRequest(BaseModel):
    code: str
    language: str
    cursor_line: int
    cursor_column: int


class AutocompleteResponse(BaseModel):
    suggestions: List[dict]


def _call_openai(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> dict:
    """Unified OpenAI API caller with error handling."""
    if not client:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if content is None:
            raise HTTPException(status_code=500, detail="AI returned empty response")
        return json.loads(content)
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")


@router.post("/explain", response_model=ExplainResponse)
async def explain_code(request: ExplainRequest):
    """
    Explain what a code snippet does in plain English.

    **Example:**
    ```json
    {
      "code": "def factorial(n): return 1 if n == 0 else n * factorial(n-1)",
      "language": "python"
    }
    ```
    """
    system_prompt = "You are a senior software engineer explaining code to junior developers. Be clear and concise."
    user_prompt = f"""Explain this {request.language} code in simple terms:

```{request.language}
{request.code}
{"Context: " + request.context if request.context else ""}

Provide:

A clear explanation (2-3 sentences)

Complexity assessment (Simple/Moderate/Complex)

2-3 improvement suggestions (if any)

Format as JSON:
{{
"explanation": "This function calculates...",
"complexity": "Simple",
"suggestions": ["Consider memoization", "Add input validation"]
}}
"""
    result = _call_openai(system_prompt, user_prompt, temperature=0.3)
    return ExplainResponse(**result)


@router.post("/translate", response_model=TranslateResponse)
async def translated_code(request: TranslateRequest):
    """
    Translate code from one language to another.
    **Supported translations:**
    - Python ↔ C ↔ Java ↔ JavaScript
    - COBOL → Python (legacy migration)
    - Assembly → C

    **Example:**
    ```json
    {
      "code": "for i in range(10): print(i)",
      "from_language": "python",
      "to_language": "c"
    }
    ```
    """
    system_prompt = "You are an expert polyglot programmer specializing in accurate code translation."
    user_prompt = f"""Translate this code from {request.from_language} to {request.to_language}.
Source code ({request.from_language}): {request.code}
Requirements:

Preserve logic exactly

Use idiomatic {request.to_language} patterns

{"Keep comments" if request.preserve_comments else "Remove comments"}

Add brief migration notes if syntax differs significantly

Return JSON:
{{
"translated_code": "... complete {request.to_language} code ...",
"notes": ["Added header includes", "Changed loop syntax"]
}}
"""
    result = _call_openai(system_prompt, user_prompt, temperature=0.2)
    return TranslateResponse(**result)


@router.post("/refactor", response_model=RefactorResponse)
async def refactored_code(request: RefactorRequest):
    """
    Suggest refactoring improvements for code quality.
    **Focus areas:**
    - `readability`: Improve naming, structure, documentation
    - `performance`: Optimize algorithms, reduce complexity
    - `security`: Fix vulnerabilities, validate inputs

    **Example:**
    ```json
    {
      "code": "def calc(x,y): return x*x+y*y",
      "language": "python",
      "focus": "readability"
    }
    ```
    """
    system_prompt = f"You are a code refactoring expert focusing on {request.focus}. Suggest practical improvements."
    user_prompt = f"""Refactor this {request.language} code focusing on {request.focus}.
Original code: {request.code}
Provide:

Refactored code (complete, executable)

List of changes with line numbers

Rationale for major changes

Format as JSON:
{{
"refactored_code": "... improved code ...",
"changes": [
{{"type": "rename", "line": 1, "description": "Renamed 'calc' to 'calculate_distance'"}},
{{"type": "extract", "line": 5, "description": "Extracted validation logic"}}
],
"rationale": "Improved naming makes the function's purpose clearer..."
}}
"""
    result = _call_openai(system_prompt, user_prompt, temperature=0.3, max_tokens=3000)
    return RefactorResponse(**result)


@router.post("/generate", response_model=GenerateResponse)
async def generate_code(request: GenerateRequest):
    """
    Generate code from natural language description.
    **Styles:**
    - `clean`: Concise, readable code
    - `documented`: Full docstrings and comments
    - `optimized`: Performance-focused implementation

    **Example:**
    ```json
    {
      "prompt": "Create a function to validate email addresses using regex",
      "language": "python",
      "style": "documented"
    }
    ```
    """
    style_guidelines = {
        "clean": "Follow clean code principles with descriptive names. Minimal comments.",
        "documented": "Include comprehensive docstrings, type hints, and inline comments.",
        "optimized": "Focus on performance and memory efficiency. Use optimal algorithms.",
    }
    system_prompt = f"You are an expert {request.language} developer who writes production-quality code."
    user_prompt = f"""Generate {request.language} code for this request:
"{request.prompt}"
Style: {style_guidelines.get(request.style, style_guidelines["clean"])}

Return JSON:
{{
"code": "... complete implementation ...",
"explanation": "Brief explanation of the approach and key decisions"
}}
"""
    result = _call_openai(system_prompt, user_prompt, temperature=0.4, max_tokens=3000)
    return GenerateResponse(**result)


@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_code(request: AutocompleteRequest):
    """
    Provide AI-powered autocomplete suggestions (real-time).
    **Usage:** Called as user types in the editor (debounced 300ms).

    **Example:**
    ```json
    {
      "code": "def calculate_sum(numbers):\\n    total = 0\\n    for num in ",
      "language": "python",
      "cursor_line": 3,
      "cursor_column": 19
    }
    ```
    """
    lines = request.code.split("\n")
    context_lines = lines[max(0, request.cursor_line - 10) : request.cursor_line]
    context = "\n".join(context_lines)
    system_prompt = "You are an AI code completion assistant. Suggest 1-3 intelligent completions based on context."
    user_prompt = f"""Given this {request.language} code, suggest the next completion(s):
    {context}
    █  <-- cursor here (line {request.cursor_line}, col {request.cursor_column})
    Provide 1-3 suggestions (function calls, variable names, control flow).
Return JSON:
{{
"suggestions": [
{{"text": "numbers:", "type": "keyword", "description": "Start for loop iteration"}},
{{"text": "range(len(numbers)):", "type": "function", "description": "Index-based iteration"}}
]
}}
"""
    try:
        result = _call_openai(
            system_prompt,
            user_prompt,
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=2000,
        )
        return AutocompleteResponse(**result)
    except Exception as e:
        print(f"⚠️ Autocomplete failed: {e}")
        return AutocompleteResponse(suggestions=[])


@router.get("/status")
async def ai_status():
    """Check if AI features are available and configured."""
    return {
        "available": client is not None,
        "model": settings.openai_model if client else None,
        "features": {
            "explain": True,
            "translate": True,
            "refactor": True,
            "generate": True,
            "autocomplete": True,
            "chat": True,
        },
        "limits": {
            "rate_limit": "60 requests/minute",
            "max_code_length": 8000,
            "max_tokens": 4000,
        },
    }
