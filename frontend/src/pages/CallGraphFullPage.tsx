import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Network, 
  ArrowLeft, 
  Maximize2, 
  Minimize2, 
  Loader2, 
  AlertTriangle 
} from 'lucide-react';
import callGraphApi, { CallGraph } from '../services/callGraphApi';
import DependencyGraph from '../components/DependencyGraph';

const CallGraphFullPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [callGraph, setCallGraph] = useState<CallGraph | null>(null);

  useEffect(() => {
    if (id) {
      loadData();
    }
  }, [id]);

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      // We only need the call graph data for this view
      const data = await callGraphApi.getCallGraph(id);
      setCallGraph(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load call graph data");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-screen w-screen bg-slate-50 dark:bg-slate-900 flex flex-col items-center justify-center">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
        <p className="text-slate-600 dark:text-slate-400">Loading full graph...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen w-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center p-4">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 max-w-md w-full">
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
            <p className="text-red-800 dark:text-red-300 font-semibold">Error Loading Graph</p>
          </div>
          <p className="text-slate-600 dark:text-slate-400 mb-6">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="w-full py-2 px-4 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 rounded-lg transition-colors font-medium text-slate-700 dark:text-slate-200"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-slate-50 dark:bg-slate-900 flex flex-col overflow-hidden relative">
      {/* Header Toolbar */}
      <div className="absolute top-4 left-4 right-4 z-10 flex justify-between items-center pointer-events-none">
        <div className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm shadow-lg border border-slate-200 dark:border-slate-700 rounded-xl p-2 pointer-events-auto flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            title="Go Back"
          >
            <ArrowLeft className="w-6 h-6 text-slate-700 dark:text-slate-200" />
          </button>
          
          <div className="h-6 w-px bg-slate-200 dark:bg-slate-700"></div>
          
          <div className="flex items-center gap-2 px-2">
            <Network className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h1 className="font-bold text-slate-900 dark:text-white hidden sm:block">
              Full Call Graph
            </h1>
          </div>
        </div>

        <div className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm shadow-lg border border-slate-200 dark:border-slate-700 rounded-xl p-2 pointer-events-auto">
          <div className="text-sm font-medium text-slate-600 dark:text-slate-400 px-3">
            {callGraph?.nodes.length || 0} Nodes • {callGraph?.edges.length || 0} Edges
          </div>
        </div>
      </div>

      {/* Graph Area */}
      <div className="flex-1 w-full h-full">
        {callGraph && (
          <DependencyGraph
            nodes={callGraph.nodes.map((n) => ({
              id: n.name,
              label: n.name,
              type: n.is_external ? "external" : "internal",
              file: n.file,
            }))}
            edges={callGraph.edges.map((e) => ({
              source: e.from,
              target: e.to,
              label: `Line ${e.line}`,
            }))}
            className="w-full h-full"
          />
        )}
      </div>
    </div>
  );
};

export default CallGraphFullPage;
