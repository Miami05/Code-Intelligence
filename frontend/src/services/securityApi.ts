import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Vulnerability {
  id: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  cwe_id: string;
  owasp_category: string;
  file_path: string;
  line_number: number;
  code_snippet: string;
  description: string;
  recommendation: string;
  confidence: 'high' | 'medium' | 'low';
  created_at: string;
}

export interface SecurityStats {
  repository_id: string;
  total_vulnerabilities: number;
  by_severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  by_type: Record<string, number>;
}

export interface VulnerabilitiesResponse {
  repository_id: string;
  total_vulnerabilities: number;
  vulnerabilities: Vulnerability[];
}

export const securityApi = {
  /**
   * Trigger security scan for repository
   */
  async scanRepository(repositoryId: string): Promise<{ status: string; message: string }> {
    const response = await axios.post(`${API_URL}/api/security/repositories/${repositoryId}/scan`);
    return response.data;
  },

  /**
   * Get all vulnerabilities for repository
   */
  async getVulnerabilities(
    repositoryId: string,
    severity?: string,
    type?: string
  ): Promise<VulnerabilitiesResponse> {
    const params: any = {};
    if (severity) params.severity = severity;
    if (type) params.type = type;
    
    const response = await axios.get(
      `${API_URL}/api/security/repositories/${repositoryId}/vulnerabilities`,
      { params }
    );
    return response.data;
  },

  /**
   * Get security statistics for repository
   */
  async getSecurityStats(repositoryId: string): Promise<SecurityStats> {
    const response = await axios.get(
      `${API_URL}/api/security/repositories/${repositoryId}/security-stats`
    );
    return response.data;
  },
};
