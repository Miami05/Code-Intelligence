from typing import List, Optional

import numpy as np
from openai import OpenAI

from config import settings

client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# OpenAI limits
MAX_BATCH_SIZE = 2048  # Max inputs per request
MAX_TEXT_LENGTH = 8191  # Max tokens (~32k chars)


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
        raise ValueError("Text cannot be empty")
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
    Generate embeddings for multiple texts in batches.
    
    OpenAI has a limit of 2048 inputs per request, so we chunk large batches.

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
    
    # Filter and clean texts
    valid_texts = []
    for text in texts:
        if text and isinstance(text, str) and text.strip():
            # Truncate to OpenAI's limit
            cleaned = text.strip()[:MAX_TEXT_LENGTH * 4]  # ~4 chars per token
            valid_texts.append(cleaned)
        else:
            # Use placeholder for empty texts
            valid_texts.append("[empty]")
    
    if not valid_texts:
        print("⚠️  No valid texts to embed")
        return []
    
    model = model or settings.openai_model
    all_embeddings = []
    
    # Process in chunks of MAX_BATCH_SIZE
    total_batches = (len(valid_texts) + MAX_BATCH_SIZE - 1) // MAX_BATCH_SIZE
    
    try:
        for i in range(0, len(valid_texts), MAX_BATCH_SIZE):
            batch = valid_texts[i:i + MAX_BATCH_SIZE]
            batch_num = (i // MAX_BATCH_SIZE) + 1
            
            print(f"📊 Batch {batch_num}/{total_batches}: Generating {len(batch)} embeddings...")
            
            response = client.embeddings.create(input=batch, model=model)
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)
            
            print(f"✅ Batch {batch_num}/{total_batches}: Generated {len(embeddings)} embeddings")
        
        print(f"✅ Total: Generated {len(all_embeddings)} embeddings")
        return all_embeddings
        
    except Exception as e:
        print(f"❌ Error generating batch embeddings: {e}")
        # Log details for debugging
        print(f"   Total texts: {len(valid_texts)}")
        print(f"   Batch size: {MAX_BATCH_SIZE}")
        if valid_texts:
            print(f"   Sample texts (first 3): {[t[:100] for t in valid_texts[:3]]}")
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
