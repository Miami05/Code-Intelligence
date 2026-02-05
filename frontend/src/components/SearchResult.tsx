import type { SearchResult } from "../services/api";
import { FileCode, Package, Target, ExternalLink } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

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
      <div className="text-center py-12 bg-slate-800/50 rounded-lg border border-slate-700">
        <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <p className="text-gray-400 text-lg font-medium">No results found for "{query}"</p>
        <p className="text-gray-500 text-sm mt-2">
          Try lowering the similarity threshold or using different keywords
        </p>
      </div>
    );
  }

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      function: "bg-blue-500/20 text-blue-300 border-blue-500/30",
      class_: "bg-purple-500/20 text-purple-300 border-purple-500/30",
      method: "bg-green-500/20 text-green-300 border-green-500/30",
      variable: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
    };
    return colors[type] || "bg-gray-500/20 text-gray-300 border-gray-500/30";
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.7) return "text-green-400 bg-green-400/10";
    if (similarity >= 0.5) return "text-yellow-400 bg-yellow-400/10";
    return "text-orange-400 bg-orange-400/10";
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">
          Found <span className="text-blue-400">{results.length}</span> result{results.length !== 1 ? "s" : ""}
        </h2>
        <p className="text-sm text-gray-400">
          Searched for: <span className="text-gray-300 font-medium">"{query}"</span>
        </p>
      </div>

      {results.map((result, index) => (
        <div
          key={result.symbol_id}
          className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-blue-500/50 
                   transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/10
                   animate-fadeIn"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3 flex-1">
              <FileCode className="w-5 h-5 text-blue-400" />
              <h3 className="text-lg font-mono font-semibold text-white truncate">
                {result.name}
              </h3>
              <span
                className={`px-2 py-1 rounded text-xs font-medium border ${getTypeColor(result.type)}`}
              >
                {result.type}
              </span>
            </div>

            <div className="flex items-center space-x-2 ml-4">
              <div className={`flex items-center gap-1 px-2 py-1 rounded ${getSimilarityColor(result.similarity).split(' ')[1]}`}>
                <Target className="w-4 h-4" />
                <span
                  className={`font-mono font-semibold text-sm ${getSimilarityColor(result.similarity).split(' ')[0]}`}
                >
                  {(result.similarity * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Signature with Syntax Highlighting */}
          <div className="mb-3 rounded-lg overflow-hidden border border-slate-700">
            <SyntaxHighlighter
              language="python"
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                padding: '12px',
                background: '#0f172a',
                fontSize: '0.875rem',
              }}
              wrapLongLines
            >
              {result.signature || result.name}
            </SyntaxHighlighter>
          </div>

          {/* Metadata */}
          <div className="flex items-center flex-wrap gap-4 text-sm text-gray-400">
            <div className="flex items-center gap-1">
              <span>📄</span>
              <code className="text-gray-300 bg-slate-900 px-2 py-0.5 rounded text-xs">
                {result.file_path}
              </code>
            </div>
            {result.lines && (
              <div className="flex items-center gap-1">
                <span>📍</span>
                <span className="text-gray-400">Lines {result.lines}</span>
              </div>
            )}
            {result.repository_id && (
              <div className="flex items-center gap-1 text-blue-400 hover:text-blue-300 cursor-pointer">
                <ExternalLink className="w-3 h-3" />
                <span className="text-xs">View in repo</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
