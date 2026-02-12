from typing import List, Optional

from pydantic import BaseModel


class SearchResult(BaseModel):
    symbo_id: str
    name: str
    type: str
    signature: str = ""
    file_path: str
    repository_id: str
    language: str
    similiarity: Optional[float] = None
    lines: Optional[str] = None
    cyclomatic_complexity: Optional[int] = None
    maintainability_index: Optional[float] = None

    class Config:
        from_attributes = None


class SearchResponses(BaseModel):
    query: str
    threshold: float
    total_results: int
    results: List[SearchResult]
