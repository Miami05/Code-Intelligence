import axios from 'axios';
import { GitHubRepository, GitHubImportRequest, GitHubImportResponse, GitHubValidateResponse, GitHubStats } from '../types/github';

const API_BASE_URL = 'http://localhost:8000/api';

export const githubApi = {
  // Validate GitHub URL
  validateURL: async (url: string): Promise<GitHubValidateResponse> => {
    const response = await axios.post<GitHubValidateResponse>(
      `${API_BASE_URL}/github/validate`,
      null,
      { params: { url } }
    );
    return response.data;
  },

  // Import GitHub repository
  importRepository: async (data: GitHubImportRequest): Promise<GitHubImportResponse> => {
    const response = await axios.post<GitHubImportResponse>(
      `${API_BASE_URL}/github/import`,
      data
    );
    return response.data;
  },

  // List GitHub repositories
  listRepositories: async (limit = 50, offset = 0): Promise<{ repositories: GitHubRepository[] }> => {
    const response = await axios.get(
      `${API_BASE_URL}/github/repositories`,
      { params: { limit, offset } }
    );
    return response.data;
  },

  // Get specific GitHub repository
  getRepository: async (id: string): Promise<GitHubRepository> => {
    const response = await axios.get<GitHubRepository>(
      `${API_BASE_URL}/github/repositories/${id}`
    );
    return response.data;
  },

  // Delete GitHub repository
  deleteRepository: async (id: string): Promise<void> => {
    await axios.delete(`${API_BASE_URL}/github/repositories/${id}`);
  },

  // Get GitHub statistics
  getStats: async (): Promise<GitHubStats> => {
    const response = await axios.get<GitHubStats>(
      `${API_BASE_URL}/github/stats`
    );
    return response.data;
  },
};
