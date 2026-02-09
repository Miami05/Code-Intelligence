export type Language = "python" | "c" | "assembly" | "cobol";

export interface SearchResult {
  symbol_id: string;
  name: string;
  type: string;
  signature: string;
  file_path: string;
  repository_id: string;
  language: Language; // NEW: Language field
  similarity: number;
  lines?: string;
}

export interface SearchResponse {
  query: string;
  threshold: number;
  total_results: number;
  results: SearchResult[];
}

export interface LanguageStats {
  language: Language;
  file_count: number;
  symbol_count: number;
}

export interface StatsResponse {
  total_repositories: number;
  total_files: number;
  total_symbols: number;
  total_embeddings: number;
  coverage: number;
  enabled: boolean;
  language_breakdown: LanguageStats[];
}
