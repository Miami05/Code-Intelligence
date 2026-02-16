import axios from 'axios';
import {
  Repository,
  RepositoryFile,
  RepositorySymbol,
  QualityDashboard,
  ComplexFunction,
  FileContent,
} from '../types/repository';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const repositoryApi = {
  // List repositories
  async list(limit = 10, offset = 0): Promise<{ total: number; repositories: Repository[] }> {
    const response = await api.get('/repositories', {
      params: { limit, offset },
    });
    return response.data;
  },

  // Get repository by ID
  async getById(id: string): Promise<Repository> {
    const response = await api.get(`/repositories/${id}`);
    return response.data;
  },

  // Get repository files
  async getFiles(
    id: string,
    language?: string,
    limit = 100
  ): Promise<{ repository_id: string; total_files: number; files: RepositoryFile[] }> {
    const response = await api.get(`/repositories/${id}/files`, {
      params: { language, limit },
    });
    return response.data;
  },

  // Get file content
  async getFileContent(id: string, filePath: string): Promise<FileContent> {
    const response = await api.get(`/repositories/${id}/files/${filePath}/content`);
    return response.data;
  },

  // Get repository symbols
  async getSymbols(
    id: string,
    language?: string,
    type?: string,
    limit = 100
  ): Promise<{
    repository_id: string;
    total_symbols: number;
    symbols: RepositorySymbol[];
  }> {
    const response = await api.get(`/repositories/${id}/symbols`, {
      params: { language, type, limit },
    });
    return response.data;
  },

  // Get quality dashboard
  async getQualityDashboard(id: string): Promise<QualityDashboard> {
    const response = await api.get(`/recommendations/quality-dashboard`, {
      params: { repository_id: id },
    });
    return response.data;
  },

  // Get complex functions
  async getComplexFunctions(
    id: string,
    minComplexity = 20,
    limit = 10
  ): Promise<{ functions: ComplexFunction[] }> {
    const response = await api.get(`/recommendations/complex-functions`, {
      params: { repository_id: id, min_complexity: minComplexity, limit },
    });
    return response.data;
  },
};
