import { api } from "./api";

export interface CallGraphNode {
  name: string;
  file: string | null;
  symbol_id: number | null;
  calls: string[];
  called_by: string[];
  is_external: boolean;
}

export interface CallGraphEdge {
  from: string;
  to: string;
  file: string;
  line: number;
}

export interface CallGraph {
  nodes: CallGraphNode[];
  edges: CallGraphEdge[];
  total_functions: number;
  total_calls: number;
  repository_id: string;
}

export interface DependencyFile {
  file: string;
  language: string;
  imports: string[];
  imported_by: string[];
}

export interface DependencyGraph {
  files: DependencyFile[];
  total_files: number;
  total_dependencies: number;
  repository_id: string;
}

export interface DeadFunction {
  name: string;
  file: string;
  symbol_id: number | null;
  calls: number;
  severity: "high" | "medium" | "low";
}

export interface DeadCodeAnalysis {
  repository_id: string;
  dead_functions: DeadFunction[];
  total_dead: number;
}

export interface CircularDependency {
  cycle: string[];
  length: number;
  severity: "critical" | "high" | "medium";
}

export interface CircularDependencies {
  repository_id: string;
  circular_dependencies: CircularDependency[];
  total_cycles: number;
}

const callGraphApi = {
  /**
   * Get call graph for repository
   * Shows function call relationships
   */
  getCallGraph: async (repositoryId: string): Promise<CallGraph> => {
    const response = await api.get<CallGraph>(
      `/api/call-graph/repositories/${repositoryId}/call-graph`,
    );
    return response.data;
  },

  /**
   * Get file-level dependencies
   * Shows import/include relationships
   */
  getDependencies: async (repositoryId: string): Promise<DependencyGraph> => {
    const response = await api.get<DependencyGraph>(
      `/api/call-graph/repositories/${repositoryId}/dependencies`,
    );
    return response.data;
  },

  /**
   * Find dead code (unused functions)
   */
  getDeadCode: async (repositoryId: string): Promise<DeadCodeAnalysis> => {
    const response = await api.get<DeadCodeAnalysis>(
      `/api/call-graph/repositories/${repositoryId}/dead-code`,
    );
    return response.data;
  },

  /**
   * Find circular dependencies
   */
  getCircularDependencies: async (
    repositoryId: string,
  ): Promise<CircularDependencies> => {
    const response = await api.get<CircularDependencies>(
      `/api/call-graph/repositories/${repositoryId}/circular-deps`,
    );
    return response.data;
  },
};

export default callGraphApi;
