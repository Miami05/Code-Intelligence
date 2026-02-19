export interface CodeDuplication {
    id: string;
    repository_id: string;
    file1: {
        id: string;
        path: string;
        start_line: number;
        end_line: number;
    };
    file2: {
        id: string;
        path: string;
        start_line: number;
        end_line: number;
    };
    similarity: number;
    duplicate_lines: number;
    duplicate_tokens: number;
    code_snippet: string;
}

export interface CodeSmell {
    id: string;
    smell_type: 'long_method' | 'god_class' | 'feature_envy' | 'large_class' | 'long_parameter_list' | 'duplicate_code' | 'dead_code' | 'missing_docstring';
    severity: 'low' | 'medium' | 'high' | 'critical';
    title: string;
    description: string;
    suggestion: string;
    file: {
        id: string;
        path: string;
    };
    symbol?: {
        id: string;
        name: string;
    } | null;
    location: {
        start_line: number;
        end_line: number;
    };
    metrics?: {
        value: number;
        threshold: number;
    };
}

export interface UndocumentedSymbol {
    id: string;
    name: string;
    type: string;
    file: string;
    line: number;
}

export interface AutoDocResult {
    symbol_id: string;
    symbol_name: string;
    docstring: string;
    insert_line: number;
    file_id: string;
    file_path: string;
}

export interface MetricsSnapshot {
    id: string;
    repository_id: string;
    quality_score: number;
    total_files: number;
    total_lines: number;
    avg_complexity: number;
    duplication_percentage: number;
    code_smells_count: number;
    vulnerability_count: number;
    created_at: string;
}

export interface AnalysisStatus {
    repository_id: string;
    status: 'started' | 'completed' | 'failed';
    message: string;
    tasks?: string[];
}
