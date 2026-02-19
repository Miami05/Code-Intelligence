import axios from 'axios';
import { 
    CodeDuplication, 
    CodeSmell, 
    UndocumentedSymbol, 
    AutoDocResult,
    MetricsSnapshot,
    AnalysisStatus
} from '../types/analysis';

// Use configured API base URL or default
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const analysisService = {
    /**
     * Trigger a full analysis scan (Duplications + Code Smells + Metrics)
     */
    runFullScan: async (repoId: string): Promise<AnalysisStatus> => {
        const response = await api.post(`/api/analysis/full-scan/${repoId}`);
        return response.data;
    },

    /**
     * Get code duplications
     */
    getDuplications: async (repoId: string, minSimilarity = 0.8): Promise<{ duplications: CodeDuplication[] }> => {
        const response = await api.get(`/api/analysis/duplications/${repoId}`, {
            params: { min_similarity: minSimilarity }
        });
        return response.data;
    },

    /**
     * Get code smells
     */
    getCodeSmells: async (repoId: string, severity?: string, smellType?: string): Promise<{ code_smells: CodeSmell[] }> => {
        const response = await api.get(`/api/analysis/code-smells/${repoId}`, {
            params: { severity, smell_type: smellType }
        });
        return response.data;
    },

    /**
     * Get undocumented symbols (Sprint 9)
     */
    getUndocumentedSymbols: async (repoId: string): Promise<{ undocumented_symbols: UndocumentedSymbol[], count: number }> => {
        const response = await api.get(`/api/analysis/undocumented/${repoId}`);
        return response.data;
    },

    /**
     * Generate auto-documentation (Sprint 9)
     */
    generateDocumentation: async (repoId: string, maxFiles = 10): Promise<{ documentation: AutoDocResult[] }> => {
        const response = await api.post(`/api/analysis/auto-document/${repoId}`, null, {
            params: { max_files: maxFiles }
        });
        return response.data;
    },

    /**
     * Get metrics history
     */
    getMetricsHistory: async (repoId: string): Promise<{ snapshots: MetricsSnapshot[] }> => {
        const response = await api.get(`/api/analysis/metrics/${repoId}/history`);
        return response.data;
    }
};
