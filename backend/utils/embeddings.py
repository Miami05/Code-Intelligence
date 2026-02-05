from typing import List, Optional

import numpy as np
from openai import OpenAI

from config import settings

client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def generate_embedding(text: str, model: Optional[str] = None) -> List[float]:
    """
    Generate embedding vector for a text string using OpenAI API.

    Args:
        text: Text to embed (code signature, function name, etc.)
        model: OpenAI model name (defaults to settings)

    Returns:
        List of floats representing the embedding vector
    """
    if not client:
        raise ValueError("OpenAI API key not configured")
    if not text or not text.strip():
        raise ValueError("Text cannot be emtpy")
    model = model or settings.openai_model
    try:
        response = client.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        raise


def generate_embeddings_batch(
    texts: List[str], model: Optional[str] = None
) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in a single API call.

    Args:
        texts: List of text strings to embed
        model: OpenAI model name (defaults to settings)

    Returns:
        List of embedding vectors
    """
    if not client:
        raise ValueError("OpenAI API key not configured")
    if not texts:
        return []
    texts = [t.strip() for t in texts if t and t.strip()]
    if not texts:
        return []
    model = model or settings.openai_model
    try:
        response = client.embeddings.create(input=texts, model=model)
        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"❌ Error generating batch embeddings: {e}")
        raise


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score between -1 and 1 (1 = identical)
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))


def prepare_symbol_for_embedding(
    symbol_name: str, symbol_type: str, signature: Optional[str] = None
) -> str:
    """
    Create a rich text representation of a code symbol for embedding.

    Args:
        symbol_name: Name of the symbol (function/class name)
        symbol_type: Type of symbol (function, class, etc.)
        signature: Full signature if available

    Returns:
        Formatted string optimized for embedding
    """
    parts = [f"{symbol_type}: {symbol_name}"]
    if signature:
        parts.append(signature)
    return " | ".join(parts)
