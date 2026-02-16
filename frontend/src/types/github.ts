export interface GitHubValidateResponse {
  valid: boolean;
  owner?: string;
  repo?: string;
  branch?: string;
  url: string;
  error?: string;
}

export interface GitHubImportRequest {
  url: string;
  branch?: string;
  token?: string;
}

export interface GitHubImportResponse {
  repository_id: string;
  owner: string;
  repo: string;
  branch: string;
  status: string;
  task_id: string;
  message: string;
}

export interface GitHubRepository {
  id: string;
  name: string;
  owner: string;
  repo: string;
  github_url: string;
  branch: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  file_count: number;
  symbol_count: number;
  github_stars?: number;
  github_language?: string;
  created_at: string;
}

export interface GitHubStats {
  total_repositories: number;
  completed: number;
  failed: number;
  processing: number;
  total_files: number;
  total_symbols: number;
}
