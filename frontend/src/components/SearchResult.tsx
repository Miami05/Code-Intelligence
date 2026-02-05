import React from "react";
import { SearchResult } from "../services/api";
import { FileCode, Package, Target } from "lucide-react";

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
      <div className="text-center py-12">
        <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <p className="text-gray-400 text-lg">No results found for "{query}"</p>
        <p className="text-gray-500 text-sm mt-2">
          Try lowering the similarity threshold or using different keywords
        </p>
      </div>
    );
  }

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      function: "bg-blue-500/20 text-blue-300",
      class_: "bg-purple-500/20 text-purple-300",
      method: "bg-green-500/20 text-green-300",
      variable: "bg-yellow-500/20 text-yellow-300",
    };
    return colors[type] || "bg-gray-500/20 text-gray-300";
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.7) return "text-green-400";
    if (similarity >= 0.5) return "text-yellow-400";
    return "text-orange-400";
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">
          Found {results.length} result{results.length !== 1 ? "s" : ""}
        </h2>
      </div>

      {results.map((result) => (
        <div
          key={result.symbol_id}
          className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-primary 
                   transition-colors duration-200"
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <FileCode className="w-5 h-5 text-primary" />
              <h3 className="text-lg font-mono font-semibold text-white">
                {result.name}
              </h3>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${getTypeColor(result.type)}`}
              >
                {result.type}
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4 text-gray-400" />
              <span
                className={`font-mono font-semibold ${getSimilarityColor(result.similarity)}`}
              >
                {(result.similarity * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Signature */}
          <div className="bg-slate-900 rounded p-3 mb-3 overflow-x-auto">
            <code className="text-sm text-gray-300 font-mono">
              {result.signature}
            </code>
          </div>

          {/* Metadata */}
          <div className="flex items-center space-x-4 text-sm text-gray-400">
            <span>📄 {result.file_path}</span>
            {result.lines && <span>📍 Lines {result.lines}</span>}
          </div>
        </div>
      ))}
    </div>
  );
};
