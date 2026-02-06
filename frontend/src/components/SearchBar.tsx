import { useState } from "react";
import { Search, Loader2, Sparkles } from "lucide-react";

interface SearchBarProps {
  onSearch: (query: string, threshold: number) => void;
  isLoading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  isLoading,
}) => {
  const [query, setQuery] = useState("");
  const [threshold, setThreshold] = useState(0.4);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, threshold);
    }
  };

  const exampleQueries = [
    "functions that handle authentication",
    "database connection setup",
    "calculate totals",
    "parse JSON data",
  ];

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Main Search Input */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="w-6 h-6 text-gray-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your codebase with natural language..."
            className="w-full pl-14 pr-4 py-5 text-lg bg-white dark:bg-gray-900 border-2 border-gray-200 dark:border-gray-700 rounded-2xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 dark:focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all shadow-sm hover:shadow-md"
            disabled={isLoading}
          />
        </div>

        {/* Example Queries */}
        {!query && (
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Sparkles className="w-4 h-4" />
              Try:
            </span>
            {exampleQueries.map((example, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setQuery(example)}
                className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg transition-colors border border-gray-200 dark:border-gray-700"
              >
                {example}
              </button>
            ))}
          </div>
        )}

        {/* Threshold Control */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
              Similarity Threshold:
            </label>
            <div className="flex items-center gap-3 flex-1">
              <input
                type="range"
                min="0.2"
                max="0.9"
                step="0.1"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                disabled={isLoading}
              />
              <span className="px-3 py-1 text-sm font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 min-w-[60px] text-center">
                {(threshold * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>

        {/* Search Button */}
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-300 dark:disabled:from-gray-700 dark:disabled:to-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/40 disabled:shadow-none flex items-center justify-center gap-3 text-lg"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              <span>Searching...</span>
            </>
          ) : (
            <>
              <Search className="w-6 h-6" />
              <span>Search Code</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
