import axios from 'axios';
import { Repository, RepositoryFile, RepositorySymbol } from '../types/repository';

const API_BASE_URL = 'http://localhost:8000/api';

export const repositoryApi = {
  // List all repositories (GitHub + Upload)
  listAll: async (limit = 50, offset = 0) => {
    const response = await axios.get(`${API_BASE_URL}/repositories`, {
      params: { limit, offset },
    });
    return response.data;
  },

  // Get repository details
  getById: async (id: string): Promise<Repository> => {
    const response = await axios.get<Repository>(
      `${API_BASE_URL}/repositories/${id}`
    );
    return response.data;
  },

  // Get repository files
  getFiles: async (id: string, language?: string, limit = 100) => {
    const response = await axios.get(`${API_BASE_URL}/repositories/${id}/files`, {
      params: { language, limit },
    });
    return response.data;
  },

  // Get repository symbols
  getSymbols: async (id: string, language?: string, type?: string, limit = 100) => {
    const response = await axios.get(`${API_BASE_URL}/repositories/${id}/symbols`, {
      params: { language, type, limit },
    });
    return response.data;
  },

  // Get quality dashboard
  getQualityDashboard: async (repositoryId?: string) => {
    const response = await axios.get(`${API_BASE_URL}/recommendations/quality-dashboard`, {
      params: { repository_id: repositoryId },
    });
    return response.data;
  },

  // Get complex functions
  getComplexFunctions: async (repositoryId?: string, minComplexity = 20, limit = 50) => {
    const response = await axios.get(`${API_BASE_URL}/recommendations/complex-functions`, {
      params: { repository_id: repositoryId, min_complexity: minComplexity, limit },
    });
    return response.data;
  },

  // Get low maintainability functions
  getLowMaintainability: async (repositoryId?: string, maxIndex = 65, limit = 50) => {
    const response = await axios.get(`${API_BASE_URL}/recommendations/low-maintainability`, {
      params: { repository_id: repositoryId, max_index: maxIndex, limit },
    });
    return response.data;
  },
};
