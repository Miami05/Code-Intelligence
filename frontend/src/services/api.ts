import axios from "axios";
import { Language, SearchResponse } from "../types/api";

const API_BASE_URL = "http://localhost:8000/api";

export interface SearchParams {
  query: string;
  threshold?: number;
  limit?: number;
  language?: Language;
}

export const searchAPI = {
  semanticSearch: async (params: SearchParams): Promise<SearchResponse> => {
    const { query, threshold = 0.4, limit = 20, language } = params;

    const requestParams: any = {
      query,
      threshold,
      limit,
    };

    if (language) {
      requestParams.language = language;
    }

    const response = await axios.post<SearchResponse>(
      `${API_BASE_URL}/search/semantic`,
      null,
      {
        params: requestParams,
      },
    );
    return response.data;
  },
};

// Re-export types for backward compatibility
export type { SearchResult, SearchResponse } from "../types/api";
