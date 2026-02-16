export interface Repository {
  id: string;
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  file_count: number;
  symbol_count: number;
  upload_path?: string;
  created_at: string;
  // GitHub fields
  github_url?: string;
  github_owner?: string;
  github_repo?: string;
  github_branch?: string;
  github_stars?: number;
  github_language?: string;
}

export interface RepositoryFile {
  id: string;
  file_path: string;
  language: string;
  line_count: number;
  created_at: string;
}

export interface RepositorySymbol {
  symbol_id: string;
  name: string;
  type: 'function' | 'class' | 'method' | 'variable';
  file_path: string;
  line_start: number;
  line_end: number;
  signature?: string;
  cyclomatic_complexity?: number;
  maintainability_index?: number;
}

export interface QualityDashboard {
  total_symbols: number;
  average_complexity: number;
  average_maintainability: number;
  high_complexity_count: number;
  low_maintainability_count: number;
  complexity_distribution: {
    'simple (1-10)': number;
    'moderate (11-20)': number;
    'complex (21-50)': number;
    'very_complex (50+)': number;
  };
  maintainability_distribution: {
    'excellent (85-100)': number;
    'good (65-84)': number;
    'fair (50-64)': number;
    'poor (<50)': number;
  };
}

export interface ComplexFunction {
  symbol_id: string;
  name: string;
  complexity: number;
  maintainability: number;
  lines: number;
  file_path: string;
  signature?: string;
}
