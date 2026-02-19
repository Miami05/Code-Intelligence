import React, { useState, useEffect } from 'react';
import { 
    CodeSmell, 
    CodeDuplication, 
    UndocumentedSymbol,
    MetricsSnapshot 
} from '../types/analysis';
import { analysisService } from '../services/analysis';
import { useParams } from 'react-router-dom';

export const AnalysisDashboard: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [loading, setLoading] = useState(false);
    const [smells, setSmells] = useState<CodeSmell[]>([]);
    const [duplications, setDuplications] = useState<CodeDuplication[]>([]);
    const [undocumented, setUndocumented] = useState<UndocumentedSymbol[]>([]);
    const [metrics, setMetrics] = useState<MetricsSnapshot[]>([]);
    const [activeTab, setActiveTab] = useState<'smells' | 'duplications' | 'docs' | 'metrics'>('smells');

    useEffect(() => {
        if (id) fetchData();
    }, [id]);

    const fetchData = async () => {
        if (!id) return;
        setLoading(true);
        try {
            const [smellsData, dupsData, undocData, metricsData] = await Promise.all([
                analysisService.getCodeSmells(id),
                analysisService.getDuplications(id),
                analysisService.getUndocumentedSymbols(id),
                analysisService.getMetricsHistory(id)
            ]);
            setSmells(smellsData.code_smells);
            setDuplications(dupsData.duplications);
            setUndocumented(undocData.undocumented_symbols);
            setMetrics(metricsData.snapshots);
        } catch (error) {
            console.error("Failed to fetch analysis data", error);
        } finally {
            setLoading(false);
        }
    };

    const triggerScan = async () => {
        if (!id) return;
        setLoading(true);
        try {
            await analysisService.runFullScan(id);
            alert("Analysis started! Results will appear shortly.");
            // Poll for results or wait a bit
            setTimeout(fetchData, 5000); 
        } catch (error) {
            alert("Failed to start scan");
        } finally {
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
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-center">Loading analysis...</div>;

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Code Analysis Dashboard</h1>
                <div className="space-x-4">
                    <button 
                        onClick={triggerScan}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                        Run Full Scan
                    </button>
                    <button 
                        onClick={generateDocs}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                    >
                        Auto-Document ({undocumented.length} pending)
                    </button>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex space-x-4 border-b mb-6">
                {['smells', 'duplications', 'docs', 'metrics'].map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab as any)}
                        className={`py-2 px-4 capitalize ${activeTab === tab ? 'border-b-2 border-blue-500 font-bold' : 'text-gray-500'}`}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {/* Content */}
            <div className="bg-white shadow rounded p-4">
                {activeTab === 'smells' && (
                    <div>
                        <h2 className="text-xl font-semibold mb-4">Code Smells ({smells.length})</h2>
                        <div className="space-y-4">
                            {smells.map(smell => (
                                <div key={smell.id} className="border p-4 rounded hover:bg-gray-50">
                                    <div className="flex justify-between">
                                        <span className={`px-2 py-1 rounded text-sm ${
                                            smell.severity === 'critical' ? 'bg-red-100 text-red-800' : 
                                            smell.severity === 'high' ? 'bg-orange-100 text-orange-800' : 'bg-gray-100'
                                        }`}>
                                            {smell.severity.toUpperCase()}
                                        </span>
                                        <span className="text-gray-500 text-sm">{smell.smell_type}</span>
                                    </div>
                                    <h3 className="font-medium mt-2">{smell.title}</h3>
                                    <p className="text-gray-600 mt-1">{smell.description}</p>
                                    <p className="text-sm text-blue-600 mt-2">Suggested Fix: {smell.suggestion}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'duplications' && (
                    <div>
                        <h2 className="text-xl font-semibold mb-4">Code Duplications ({duplications.length})</h2>
                        {duplications.map(dup => (
                            <div key={dup.id} className="border p-4 mb-4 rounded">
                                <div className="flex justify-between mb-2">
                                    <span className="font-bold text-red-600">{dup.similarity}% Similarity</span>
                                    <span className="text-gray-500">{dup.duplicate_lines} lines</span>
                                </div>
                                <div className="grid grid-cols-2 gap-4 text-sm bg-gray-50 p-2 rounded">
                                    <div>File 1: {dup.file1.path}:{dup.file1.start_line}</div>
                                    <div>File 2: {dup.file2.path}:{dup.file2.start_line}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {activeTab === 'docs' && (
                    <div>
                        <h2 className="text-xl font-semibold mb-4">Undocumented Symbols ({undocumented.length})</h2>
                        <table className="min-w-full text-left">
                            <thead>
                                <tr className="border-b">
                                    <th className="py-2">Name</th>
                                    <th className="py-2">Type</th>
                                    <th className="py-2">File</th>
                                    <th className="py-2">Line</th>
                                </tr>
                            </thead>
                            <tbody>
                                {undocumented.map(sym => (
                                    <tr key={sym.id} className="border-b hover:bg-gray-50">
                                        <td className="py-2">{sym.name}</td>
                                        <td className="py-2">{sym.type}</td>
                                        <td className="py-2 text-gray-500 text-sm">{sym.file}</td>
                                        <td className="py-2">{sym.line}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
                
                {activeTab === 'metrics' && (
                     <div>
                        <h2 className="text-xl font-semibold mb-4">Quality Metrics History</h2>
                        <div className="space-y-2">
                            {metrics.map(m => (
                                <div key={m.id} className="flex justify-between items-center border-b py-2">
                                    <div>
                                        <span className="text-gray-900 font-medium">Score: {m.quality_score}</span>
                                        <span className="text-gray-500 text-sm ml-2">({new Date(m.created_at).toLocaleString()})</span>
                                    </div>
                                    <div className="text-sm text-gray-600">
                                        Smells: {m.code_smells_count} | Duplication: {m.duplication_percentage}% | Complexity: {m.avg_complexity}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
