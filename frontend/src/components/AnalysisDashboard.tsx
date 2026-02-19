import React, { useState, useEffect, useCallback } from 'react';
import { 
    CodeSmell, 
    CodeDuplication, 
    UndocumentedSymbol,
    MetricsSnapshot 
} from '../types/analysis';
import { analysisService } from '../services/analysis';
import { useParams } from 'react-router-dom';
import { AlertTriangle, Copy, FileText, Activity, RefreshCw, CheckCircle, Clock } from 'lucide-react';

export const AnalysisDashboard: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [loading, setLoading] = useState(false);
    const [smells, setSmells] = useState<CodeSmell[]>([]);
    const [duplications, setDuplications] = useState<CodeDuplication[]>([]);
    const [undocumented, setUndocumented] = useState<UndocumentedSymbol[]>([]);
    const [metrics, setMetrics] = useState<MetricsSnapshot[]>([]);
    const [activeTab, setActiveTab] = useState<'smells' | 'duplications' | 'docs' | 'metrics'>('smells');

    const fetchData = useCallback(async () => {
        if (!id) return;
        setLoading(true);
        try {
            const [smellsData, dupsData, undocData, metricsData] = await Promise.all([
                analysisService.getCodeSmells(id),
                analysisService.getDuplications(id),
                analysisService.getUndocumentedSymbols(id),
                analysisService.getMetricsHistory(id)
            ]);

            // Deduplicate results based on ID or content to prevent UI glitches
            const uniqueSmells = Array.from(new Map(smellsData.code_smells.map(item => [item.id, item])).values());
            const uniqueDups = Array.from(new Map(dupsData.duplications.map(item => [item.id, item])).values());
            // For undocumented symbols, use a composite key if ID is missing or duplicate
            const uniqueUndoc = Array.from(new Map(undocData.undocumented_symbols.map(item => [item.id || `${item.file}-${item.line}-${item.name}`, item])).values());
            
            setSmells(uniqueSmells);
            setDuplications(uniqueDups);
            setUndocumented(uniqueUndoc);
            setMetrics(metricsData.snapshots);
        } catch (error) {
            console.error("Failed to fetch analysis data", error);
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        if (id) fetchData();
    }, [id, fetchData]);

    const triggerScan = async () => {
        if (!id) return;
        setLoading(true);
        try {
            await analysisService.runFullScan(id);
            // Poll for results
            setTimeout(fetchData, 2000); 
        } catch (error) {
            alert("Failed to start scan");
            setLoading(false);
        }
    };

    const generateDocs = async () => {
        if (!id) return;
        setLoading(true);
        try {
            const res = await analysisService.generateDocumentation(id);
            alert(`Generated documentation for ${res.documentation.length} symbols!`);
            fetchData();
        } catch (error) {
            alert("Failed to generate documentation");
            setLoading(false);
        }
    };

    const tabs = [
        { id: 'smells', label: 'Code Smells', icon: AlertTriangle, count: smells.length },
        { id: 'duplications', label: 'Duplications', icon: Copy, count: duplications.length },
        { id: 'docs', label: 'Documentation', icon: FileText, count: undocumented.length },
        { id: 'metrics', label: 'Metrics', icon: Activity, count: metrics.length },
    ];

    if (loading && smells.length === 0 && duplications.length === 0) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 md:p-12">
            <div className="max-w-7xl mx-auto">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Code Analysis Dashboard</h1>
                        <p className="text-slate-600 dark:text-slate-400 mt-1">
                            Comprehensive quality insights for your repository
                        </p>
                    </div>
                    <div className="flex gap-3">
                        <button 
                            onClick={triggerScan}
                            disabled={loading}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors disabled:opacity-50"
                        >
                            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                            Run Full Scan
                        </button>
                        <button 
                            onClick={generateDocs}
                            disabled={loading || undocumented.length === 0}
                            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors disabled:opacity-50"
                        >
                            <CheckCircle className="w-4 h-4" />
                            Auto-Document ({undocumented.length})
                        </button>
                    </div>
                </div>

                {/* Tabs */}
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 mb-6">
                    <div className="flex overflow-x-auto p-2 gap-2">
                        {tabs.map(tab => {
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id as any)}
                                    className={`flex items-center gap-2 px-4 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
                                        activeTab === tab.id 
                                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' 
                                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'
                                    }`}
                                >
                                    <Icon className="w-4 h-4" />
                                    {tab.label}
                                    <span className="ml-1 text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                                        {tab.count}
                                    </span>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Content */}
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 min-h-[400px]">
                    {activeTab === 'smells' && (
                        <div className="space-y-4">
                            {smells.length === 0 ? (
                                <EmptyState message="No code smells detected. Great job!" />
                            ) : (
                                smells.map(smell => (
                                    <div key={smell.id} className="border border-slate-200 dark:border-slate-700 rounded-lg p-5 hover:shadow-md transition-shadow dark:bg-slate-800/50">
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="flex items-center gap-3">
                                                <span className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${
                                                    smell.severity === 'critical' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : 
                                                    smell.severity === 'high' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' : 
                                                    'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                                                }`}>
                                                    {smell.severity}
                                                </span>
                                                <h3 className="font-semibold text-slate-900 dark:text-white">{smell.title}</h3>
                                            </div>
                                            <span className="text-xs text-slate-500 dark:text-slate-400 font-mono bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">
                                                {smell.smell_type}
                                            </span>
                                        </div>
                                        <p className="text-slate-600 dark:text-slate-300 mb-3">{smell.description}</p>
                                        <div className="bg-blue-50 dark:bg-blue-900/10 border-l-4 border-blue-500 p-3 rounded-r">
                                            <p className="text-sm text-blue-800 dark:text-blue-300">
                                                <span className="font-semibold">Fix:</span> {smell.suggestion}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    {activeTab === 'duplications' && (
                        <div className="space-y-4">
                            {duplications.length === 0 ? (
                                <EmptyState message="No code duplication found." />
                            ) : (
                                duplications.map(dup => (
                                    <div key={dup.id} className="border border-slate-200 dark:border-slate-700 rounded-lg p-5">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="flex items-center gap-2">
                                                <div className="h-2 w-24 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                                                    <div 
                                                        className="h-full bg-red-500 rounded-full" 
                                                        style={{ width: `${dup.similarity}%` }}
                                                    />
                                                </div>
                                                <span className="font-bold text-red-600 dark:text-red-400">{dup.similarity}% Similarity</span>
                                            </div>
                                            <span className="text-sm text-slate-500 dark:text-slate-400">
                                                {dup.duplicate_lines} duplicated lines
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded border border-slate-200 dark:border-slate-700 font-mono text-sm text-slate-700 dark:text-slate-300 break-all">
                                                {dup.file1.path}:{dup.file1.start_line}
                                            </div>
                                            <div className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded border border-slate-200 dark:border-slate-700 font-mono text-sm text-slate-700 dark:text-slate-300 break-all">
                                                {dup.file2.path}:{dup.file2.start_line}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}

                    {activeTab === 'docs' && (
                        <div>
                            {undocumented.length === 0 ? (
                                <EmptyState message="All symbols are documented." />
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="min-w-full text-left border-collapse">
                                        <thead>
                                            <tr className="border-b border-slate-200 dark:border-slate-700">
                                                <th className="py-3 px-4 text-sm font-semibold text-slate-900 dark:text-white">Name</th>
                                                <th className="py-3 px-4 text-sm font-semibold text-slate-900 dark:text-white">Type</th>
                                                <th className="py-3 px-4 text-sm font-semibold text-slate-900 dark:text-white">Location</th>
                                                <th className="py-3 px-4 text-sm font-semibold text-slate-900 dark:text-white">Line</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {undocumented.map((sym, i) => (
                                                <tr key={sym.id || i} className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                                                    <td className="py-3 px-4 font-mono text-sm text-blue-600 dark:text-blue-400 font-medium">{sym.name}</td>
                                                    <td className="py-3 px-4 text-sm text-slate-600 dark:text-slate-300">
                                                        <span className="px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded text-xs">{sym.type}</span>
                                                    </td>
                                                    <td className="py-3 px-4 text-sm text-slate-500 dark:text-slate-400 font-mono break-all">{sym.file}</td>
                                                    <td className="py-3 px-4 text-sm text-slate-500 dark:text-slate-400 font-mono">{sym.line}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}
                    
                    {activeTab === 'metrics' && (
                         <div className="space-y-4">
                            {metrics.length === 0 ? (
                                <EmptyState message="No metrics history available." />
                            ) : (
                                metrics.map(m => (
                                    <div key={m.id} className="flex justify-between items-center border border-slate-200 dark:border-slate-700 p-4 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50">
                                        <div className="flex items-center gap-4">
                                            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                                                <Activity className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                            </div>
                                            <div>
                                                <p className="text-lg font-bold text-slate-900 dark:text-white">Score: {m.quality_score}</p>
                                                <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                                                    <Clock className="w-3 h-3" />
                                                    {new Date(m.created_at).toLocaleString()}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="text-right text-sm text-slate-600 dark:text-slate-400">
                                            <p>Smells: <span className="font-medium text-slate-900 dark:text-white">{m.code_smells_count}</span></p>
                                            <p>Duplication: <span className="font-medium text-slate-900 dark:text-white">{m.duplication_percentage}%</span></p>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const EmptyState = ({ message }: { message: string }) => (
    <div className="text-center py-12">
        <div className="inline-flex p-4 bg-slate-50 dark:bg-slate-800/50 rounded-full mb-3">
            <CheckCircle className="w-8 h-8 text-green-500" />
        </div>
        <p className="text-slate-500 dark:text-slate-400">{message}</p>
    </div>
);
