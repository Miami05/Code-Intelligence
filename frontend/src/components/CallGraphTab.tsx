import React, { useState, useEffect } from "react";
import {
  Network,
  Link2,
  Trash2,
  AlertTriangle,
  Info,
  Loader2,
} from "lucide-react";
import callGraphApi, {
  CallGraph,
  DependencyGraph as DependencyGraphData,
  DeadCodeAnalysis,
  CircularDependencies,
} from "../services/callGraphApi";
import DependencyGraph from "./DependencyGraph";

interface CallGraphTabProps {
  repositoryId: string;
}

const CallGraphTab: React.FC<CallGraphTabProps> = ({ repositoryId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<
    "graph" | "deps" | "dead" | "circular"
  >("graph");

  const [callGraph, setCallGraph] = useState<CallGraph | null>(null);
  const [dependencies, setDependencies] = useState<DependencyGraphData | null>(
    null,
  );
  const [deadCode, setDeadCode] = useState<DeadCodeAnalysis | null>(null);
  const [circularDeps, setCircularDeps] = useState<CircularDependencies | null>(
    null,
  );

  useEffect(() => {
    loadData();
  }, [repositoryId]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [callGraphData, depsData, deadCodeData, circularData] =
        await Promise.all([
          callGraphApi.getCallGraph(repositoryId),
          callGraphApi.getDependencies(repositoryId),
          callGraphApi.getDeadCode(repositoryId),
          callGraphApi.getCircularDependencies(repositoryId),
        ]);

      setCallGraph(callGraphData);
      setDependencies(depsData);
      setDeadCode(deadCodeData);
      setCircularDeps(circularData);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load call graph data");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
        <p className="text-slate-600 dark:text-slate-400">
          Analyzing call graph...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
          <p className="text-red-800 dark:text-red-300 font-semibold">
            {error}
          </p>
        </div>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
      case "high":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400";
      case "medium":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400";
      default:
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400";
    }
  };

  return (
    <div>
      {/* Summary Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-slate-700 rounded-xl p-6 border border-slate-200 dark:border-slate-600 text-center">
          <Network className="w-10 h-10 text-blue-600 dark:text-blue-400 mx-auto mb-3" />
          <p className="text-3xl font-bold text-slate-900 dark:text-white mb-1">
            {callGraph?.total_functions || 0}
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Functions
          </p>
        </div>

        <div className="bg-white dark:bg-slate-700 rounded-xl p-6 border border-slate-200 dark:border-slate-600 text-center">
          <Link2 className="w-10 h-10 text-green-600 dark:text-green-400 mx-auto mb-3" />
          <p className="text-3xl font-bold text-slate-900 dark:text-white mb-1">
            {callGraph?.total_calls || 0}
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Function Calls
          </p>
        </div>

        <div className="bg-white dark:bg-slate-700 rounded-xl p-6 border border-slate-200 dark:border-slate-600 text-center">
          <Trash2 className="w-10 h-10 text-red-600 dark:text-red-400 mx-auto mb-3" />
          <p className="text-3xl font-bold text-slate-900 dark:text-white mb-1">
            {deadCode?.total_dead || 0}
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Dead Functions
          </p>
        </div>

        <div className="bg-white dark:bg-slate-700 rounded-xl p-6 border border-slate-200 dark:border-slate-600 text-center">
          <AlertTriangle className="w-10 h-10 text-orange-600 dark:text-orange-400 mx-auto mb-3" />
          <p className="text-3xl font-bold text-slate-900 dark:text-white mb-1">
            {circularDeps?.total_cycles || 0}
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Circular Dependencies
          </p>
        </div>
      </div>

      {/* View Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {[
          { id: "graph", label: "Call Graph", icon: Network },
          { id: "deps", label: "Dependencies", icon: Link2 },
          { id: "dead", label: "Dead Code", icon: Trash2 },
          { id: "circular", label: "Circular Deps", icon: AlertTriangle },
        ].map((view) => {
          const Icon = view.icon;
          return (
            <button
              key={view.id}
              onClick={() => setActiveView(view.id as any)}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                activeView === view.id
                  ? "bg-blue-600 text-white shadow-lg"
                  : "bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-600"
              }`}
            >
              <Icon className="w-5 h-5" />
              {view.label}
            </button>
          );
        })}
      </div>

      {/* View: Call Graph */}
      {activeView === "graph" && (
        <div>
          {callGraph && callGraph.nodes.length > 0 ? (
            <>
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 mb-6">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-blue-900 dark:text-blue-300">
                    <strong>Interactive Call Graph:</strong> Nodes represent
                    functions, arrows show who calls whom. Blue = internal, gray
                    = external libraries. Drag nodes to rearrange.
                  </p>
                </div>
              </div>

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
              />

              {/* Function List */}
              <div className="mt-8">
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
                  Function Details ({callGraph.nodes.length})
                </h3>
                <div className="bg-white dark:bg-slate-700 rounded-xl border border-slate-200 dark:border-slate-600 divide-y divide-slate-200 dark:divide-slate-600 max-h-96 overflow-y-auto">
                  {callGraph.nodes.slice(0, 50).map((node) => (
                    <div
                      key={node.name}
                      className="p-4 hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold text-slate-900 dark:text-white">
                          {node.name}
                        </span>
                        {node.is_external && (
                          <span className="px-2 py-1 text-xs font-semibold bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded">
                            External
                          </span>
                        )}
                      </div>
                      {node.file && (
                        <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">
                          📄 {node.file}
                        </p>
                      )}
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        Calls: {node.calls.length} | Called by:{" "}
                        {node.called_by.length}
                      </p>
                    </div>
                  ))}
                </div>
                {callGraph.nodes.length > 50 && (
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">
                    Showing first 50 of {callGraph.nodes.length} functions
                  </p>
                )}
              </div>
            </>
          ) : (
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 text-center">
              <Info className="w-12 h-12 text-blue-600 dark:text-blue-400 mx-auto mb-3" />
              <p className="text-blue-900 dark:text-blue-300">
                No function calls detected. Make sure your repository contains
                analyzable code (Python, C, Assembly, or COBOL).
              </p>
            </div>
          )}
        </div>
      )}

      {/* View: Dependencies */}
      {activeView === "deps" && (
        <div>
          {dependencies && dependencies.files.length > 0 ? (
            <>
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 mb-6">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-blue-900 dark:text-blue-300">
                    <strong>File Dependencies:</strong> Shows which files
                    import/include other files. Supports Python imports, C
                    includes, Assembly includes, and COBOL COPY statements.
                  </p>
                </div>
              </div>

              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
                Files ({dependencies.total_files}) • Dependencies (
                {dependencies.total_dependencies})
              </h3>

              <div className="bg-white dark:bg-slate-700 rounded-xl border border-slate-200 dark:border-slate-600 divide-y divide-slate-200 dark:divide-slate-600 max-h-[500px] overflow-y-auto">
                {dependencies.files.map((file) => (
                  <div
                    key={file.file}
                    className="p-4 hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-slate-900 dark:text-white">
                        {file.file}
                      </span>
                      <span className="px-2 py-1 text-xs font-semibold bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 rounded">
                        {file.language}
                      </span>
                    </div>
                    {file.imports.length > 0 && (
                      <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">
                        📥 Imports: {file.imports.join(", ")}
                      </p>
                    )}
                    {file.imported_by.length > 0 && (
                      <p className="text-xs text-slate-600 dark:text-slate-400">
                        📤 Imported by: {file.imported_by.length} file(s)
                      </p>
                    )}
                    {file.imports.length === 0 &&
                      file.imported_by.length === 0 && (
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          No dependencies
                        </p>
                      )}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 text-center">
              <Info className="w-12 h-12 text-blue-600 dark:text-blue-400 mx-auto mb-3" />
              <p className="text-blue-900 dark:text-blue-300">
                No dependencies detected in this repository.
              </p>
            </div>
          )}
        </div>
      )}

      {/* View: Dead Code */}
      {activeView === "dead" && (
        <div>
          {deadCode && deadCode.dead_functions.length > 0 ? (
            <>
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 mb-6">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-yellow-900 dark:text-yellow-300">
                    <strong>Dead Code Detected:</strong> These functions are
                    never called. Consider removing them to improve code
                    quality.
                  </p>
                </div>
              </div>

              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
                Dead Functions ({deadCode.total_dead})
              </h3>

              <div className="bg-white dark:bg-slate-700 rounded-xl border border-slate-200 dark:border-slate-600 divide-y divide-slate-200 dark:divide-slate-600">
                {deadCode.dead_functions.map((func, idx) => (
                  <div
                    key={idx}
                    className="p-4 hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-slate-900 dark:text-white">
                        {func.name}
                      </span>
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded ${getSeverityColor(func.severity)}`}
                      >
                        {func.severity.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">
                      📄 {func.file}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Makes {func.calls} call(s) but is never called
                    </p>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-6 text-center">
              <div className="text-6xl mb-4">✅</div>
              <p className="text-green-900 dark:text-green-300 font-semibold">
                No dead code detected! All functions are being used.
              </p>
            </div>
          )}
        </div>
      )}

      {/* View: Circular Dependencies */}
      {activeView === "circular" && (
        <div>
          {circularDeps && circularDeps.circular_dependencies.length > 0 ? (
            <>
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-6">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-900 dark:text-red-300">
                    <strong>Circular Dependencies Found:</strong> Functions
                    calling each other in a cycle. This can lead to infinite
                    recursion and makes code harder to understand.
                  </p>
                </div>
              </div>

              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
                Circular Dependencies ({circularDeps.total_cycles})
              </h3>

              <div className="bg-white dark:bg-slate-700 rounded-xl border border-slate-200 dark:border-slate-600 divide-y divide-slate-200 dark:divide-slate-600">
                {circularDeps.circular_dependencies.map((cycle, idx) => (
                  <div
                    key={idx}
                    className="p-4 hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-slate-900 dark:text-white">
                        Cycle {idx + 1} ({cycle.length} functions)
                      </span>
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded ${getSeverityColor(cycle.severity)}`}
                      >
                        {cycle.severity.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 font-mono">
                      {cycle.cycle.join(" → ")}
                    </p>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-6 text-center">
              <div className="text-6xl mb-4">✅</div>
              <p className="text-green-900 dark:text-green-300 font-semibold">
                No circular dependencies detected! Your call graph is acyclic.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CallGraphTab;
