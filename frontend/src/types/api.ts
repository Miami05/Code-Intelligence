export interface SearchResult {
  symbol_id: string;
  name: string;
  type: string;
  signature: string;
  file_path: string;
  repository_id: string;
  language: string;
  similarity: number;
  lines: string;
  cyclomatic_complexity: number | null;
  maintainability_index: number | null;
}

export interface SearchResponse {
  query: string;
  threshold: number;
  language: string | null;
  repository_id: string | null;
  total_results: number;
  results: SearchResult[];
}

export interface StatsResponse {
  total_symbols: number;
  total_embeddings: number;
  coverage: number;
  model: string;
  dimensions: number;
  enabled: boolean;
}

export type Language = 'python' | 'javascript' | 'typescript' | 'java' | 'go' | 'c' | 'cpp' | 'csharp' | 'ruby' | 'php' | 'swift' | 'kotlin' | 'rust';
