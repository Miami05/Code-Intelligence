"""
Sprint 12: AI Chat / RAG (Retrieval Augmented Generation)
Allows users to ask questions about their codebase using embeddings.
"""

import json
from typing import List, Optional, cast
from uuid import UUID

from config import settings
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.file import File
from models.symbol import Symbol
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
from pydantic_settings import sources
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from utils.embeddings import generate_embedding

router = APIRouter(prefix="/api/chat", tags=["chat"])

client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    repository_id: UUID
    messages: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]


@router.post("/ask", response_model=ChatResponse)
async def ask_codebase(request: ChatRequest, db: Session = Depends(get_db)):
    """
    RAG Endpoint: Ask questions about a specific repository.

    **How it works:**
    1. Generates embedding for user question
    2. Searches for relevant code using vector similarity
    3. Sends code context + question to GPT-4
    4. Returns answer with source citations

    **Example:**
    ```json
    {
      "repository_id": "ca959b51-6521-4180-b0ce-6327a4434f66",
      "message": "How does the COBOL parser handle PERFORM statements?",
      "history": []
    }
    ```
    """
    if not client:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
    try:
        query_vector = generate_embedding(request.messages)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Embedding generation failed: {str(e)}"
        )
    
    # IMPROVED QUERY: Lower threshold (0.3) and fetch more results (LIMIT 8)
    # Also prioritize file_path matches if the user asks about a specific file
    sql = text("""
        SELECT 
            s.name,
            s.type,
            s.signature,
            f.file_path,
            f.source,
            s.line_start,
            s.line_end,
            1 - (e.embedding <=> CAST(:query_vector AS vector)) as similarity
        FROM symbols s
        JOIN embeddings e ON s.id = CAST(e.symbol_id AS uuid)
        JOIN files f ON s.file_id = f.id
        WHERE f.repository_id = :repo_id
          AND 1 - (e.embedding <=> CAST(:query_vector AS vector)) > 0.3
        ORDER BY similarity DESC
        LIMIT 8
    """)
    try:
        result = db.execute(
            sql,
            {
                "query_vector": f"[{','.join(map(str, query_vector))}]",
                "repo_id": str(request.repository_id),
            },
        ).fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")
    
    if not result:
        return ChatResponse(
            answer="I couldn't find any relevant code in this repository to answer your question. Try being more specific about function names or logic.",
            sources=[],
        )
    
    context_text = ""
    source = []
    
    for row in result:
        code_segment = ""
        if row.source:
            lines = row.source.split("\n")
            
            # IMPROVED CONTEXT: Fetch 50 lines before and after the symbol
            # This captures surrounding logic, imports, and comments
            start_line = max(0, row.line_start - 50)
            end_line = min(len(lines), (row.line_end if row.line_end else row.line_start) + 50)
            
            code_segment = "\n".join(lines[start_line:end_line])
            
            context_text += (
                f"\n--- FILE: {row.file_path} ({row.type}: {row.name}) ---\n"
            )
            context_text += f"{code_segment}\n"
            context_text += (
                f"\n--- END OF CONTEXT FROM {row.file_path} ---\n"
            )
            
            source.append(
                {
                    "file": row.file_path,
                    "symbol": row.name,
                    "type": row.type,
                    "lines": f"{start_line}-{end_line}", # Show the expanded range
                    "similarity": round(float(row.similarity), 2),
                }
            )
            
    system_prompt = """You are an expert software architect analyzing a codebase.

Rules:
- Answer questions based ONLY on the provided code context
- If the answer is not in the context, say "I don't have enough context to answer that"
- Quote specific code lines when explaining logic
- Be concise but thorough
- Suggest related areas to explore if applicable
"""
    user_prompt = f"""Code Context:
{context_text}

Question: {request.messages}
"""
    try:
        messages = [{"role": "system", "content": system_prompt}]
        if request.history:
            for mssg in request.history[-4:]:
                messages.append({"role": mssg.role, "content": mssg.content})
        messages.append({"role": "user", "content": user_prompt})
        
        # INCREASED MAX TOKENS: Allow longer answers for complex explanations
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=cast(list[ChatCompletionMessageParam], messages),
            temperature=0.2,
            max_tokens=2000, 
        )
        msg = response.choices[0].message
        answer = msg.content
        if answer is None:
            raise HTTPException(status_code=500, detail="AI returned empty content")
        return ChatResponse(answer=answer, sources=source)
    except Exception as e:
        print(f"❌ OpenAI Chat Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate answer from AI")


@router.get("/repositories/{repository_id}/context")
async def get_repository_context(repository_id: UUID, db: Session = Depends(get_db)):
    """
    Get high-level repository context for chat initialization.
    Returns summary of languages, top files, complexity stats.
    """
    stats = (
        db.query(
            func.count(File.id).label("file_count"),
            func.count(Symbol.id).label("symbol_count"),
            func.avg(Symbol.cyclomatic_complexity).label("avg_complexity"),
        )
        .join(Symbol, File.id == Symbol.file_id, isouter=True)
        .filter(File.repository_id == repository_id)
        .first()
    )
    file_count = 0
    symbol_count = 0
    avg_complexity = 0.0
    if stats is not None:
        file_count = int(stats.file_count or 0)
        symbol_count = int(stats.symbol_count or 0)
        avg_complexity = float(stats.avg_complexity or 0)

    languages = (
        db.query(File.language, func.count(File.id).label("count"))
        .filter(File.repository_id == repository_id)
        .group_by(File.language)
        .all()
    )
    return {
        "repository_id": str(repository_id),
        "stats": {
            "files": file_count,
            "symbols": symbol_count,
            "avg_complexity": round(avg_complexity, 2),
        },
        "languages": {lang.language: lang.count for lang in languages},
        "chat_tips": [
            "Ask about specific functions or files",
            "Request explanations of complex logic",
            "Inquire about security patterns",
            "Ask for refactoring suggestions",
        ],
    }
