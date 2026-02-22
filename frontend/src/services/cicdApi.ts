import { api } from './api';

export interface QualityGateConfig {
  max_complexity: number;
  max_code_smells: number;
  max_critical_smells: number;
  max_vulnerabilities: number;
  max_critical_vulnerabilities: number;
  min_quality_score: number;
  max_duplication_percentage: number;
  block_on_failure: boolean;
}

export interface QualityGateCheck {
  name: string;
  passed: boolean;
  value: number;
  threshold: number;
  message: string;
}

export interface QualityGateResult {
  passed: boolean;
  block_merge: boolean;
  checks: QualityGateCheck[];
  summary: string;
  run_id?: string;
}

export interface CICDRun {
  id: string;
  repository_id: string;
  branch: string | null;
  commit_sha: string | null;
  pr_number: number | null;
  pr_title: string | null;
  triggered_by: string;
  status: string;
  quality_gate_passed: boolean | null;
  quality_gate_details: QualityGateResult | null;
  created_at: string;
  completed_at: string | null;
}

export const cicdApi = {
  getQualityGate: async (repositoryId: string): Promise<QualityGateConfig> => {
    const res = await api.get(`/api/cicd/quality-gate/${repositoryId}`);
    return res.data;
  },

  updateQualityGate: async (
    repositoryId: string,
    config: QualityGateConfig
  ): Promise<QualityGateConfig> => {
    const res = await api.put(`/api/cicd/quality-gate/${repositoryId}`, config);
    return res.data;
  },

  runQualityGate: async (repositoryId: string): Promise<QualityGateResult> => {
    const res = await api.post(`/api/cicd/quality-gate/${repositoryId}/check`);
    return res.data;
  },

  getRuns: async (repositoryId: string, limit = 20): Promise<CICDRun[]> => {
    const res = await api.get(`/api/cicd/runs/${repositoryId}`, {
      params: { limit },
    });
    return res.data;
  },

  getReportUrl: (runId: string): string => {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    return `${base}/api/cicd/report/${runId}`;
  },

  notifySlack: async (
    repositoryId: string,
    webhookUrl: string
  ): Promise<{ sent: boolean; quality_gate: boolean }> => {
    const res = await api.post('/api/cicd/notify/slack', {
      repository_id: repositoryId,
      webhook_url: webhookUrl,
    });
    return res.data;
  },

  notifyEmail: async (
    repositoryId: string,
    toEmail: string
  ): Promise<{ sent: boolean; quality_gate: boolean }> => {
    const res = await api.post('/api/cicd/notify/email', {
      repository_id: repositoryId,
      to_email: toEmail,
    });
    return res.data;
  },
};
