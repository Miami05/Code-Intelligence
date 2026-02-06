import type { SearchResult } from "../services/api";
import { FileCode, Target, Folder, Hash } from "lucide-react";

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  query,
}) => {
  if (results.length === 0) {
    return (
      <div className="text-center py-16 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-700">
        <div className="mb-4">
          <FileCode className="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto" />
        </div>
        <p className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No results found</p>
        <p className="text-gray-600 dark:text-gray-400">
          Try lowering the similarity threshold or using different keywords
        </p>
      </div>
    );
  }

  const getTypeIcon = (type: string) => {
    const icons = {
      function: "🔵",
      class_: "🟣",
      method: "🟢",
      variable: "🟡",
    };
    return icons[type as keyof typeof icons] || "⚪";
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      function: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800",
      class_: "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800",
      method: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800",
      variable: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800",
    };
    return colors[type] || "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700";
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.7) return "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700";
    if (similarity >= 0.5) return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700";
    return "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-orange-300 dark:border-orange-700";
  };

  return (
    <div className="space-y-4">
      {/* Results Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-gray-800">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {results.length} Result{results.length !== 1 ? "s" : ""}
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            for <span className="font-semibold text-gray-900 dark:text-white">"{query}"</span>
          </p>
        </div>
      </div>

      {/* Results Grid */}
      <div className="space-y-4">
        {results.map((result, index) => (
          <div
            key={result.symbol_id}
            className="group bg-white dark:bg-gray-900 border-2 border-gray-200 dark:border-gray-800 hover:border-blue-500 dark:hover:border-blue-500 rounded-2xl p-6 transition-all duration-200 hover:shadow-xl hover:shadow-blue-500/10"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-4">
              <div className="flex items-start gap-3 flex-1 min-w-0">
                <div className="text-2xl mt-1 flex-shrink-0">{getTypeIcon(result.type)}</div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 truncate">
                    {result.name}
                  </h3>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`px-3 py-1 rounded-lg text-xs font-semibold border ${getTypeColor(result.type)}`}>
                      {result.type}
                    </span>
                    <span className={`px-3 py-1 rounded-lg text-xs font-bold border flex items-center gap-1 ${getSimilarityColor(result.similarity)}`}>
                      <Target className="w-3 h-3" />
                      {(result.similarity * 100).toFixed(1)}% match
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Code Signature */}
            <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 overflow-x-auto">
              <code className="text-sm text-gray-900 dark:text-gray-100 font-mono break-all">
                {result.signature || result.name}
              </code>
            </div>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Folder className="w-4 h-4" />
                <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-xs font-mono text-gray-900 dark:text-gray-100">
                  {result.file_path}
                </code>
              </div>
              {result.lines && (
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                  <Hash className="w-4 h-4" />
                  <span className="font-medium">Lines {result.lines}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
