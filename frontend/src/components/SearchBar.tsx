import { useState } from "react";
import { Search, Loader2 } from "lucide-react";

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
  const [searchHistory, setSearchHistory] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, threshold);
      // Add to history (keep last 5)
      setSearchHistory(prev => {
        const newHistory = [query, ...prev.filter(q => q !== query)];
        return newHistory.slice(0, 5);
      });
    }
  };

  const handleHistoryClick = (historicalQuery: string) => {
    setQuery(historicalQuery);
    onSearch(historicalQuery, threshold);
  };

  return (
    <div className="w-full max-w-4xl mx-auto mb-8">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., 'functions that calculate totals' or 'database connection classes'"
            className="w-full pl-12 pr-4 py-4 bg-slate-800 border border-slate-700 rounded-lg 
                     text-white placeholder-gray-400 focus:outline-none focus:ring-2 
                     focus:ring-blue-500 focus:border-transparent text-lg transition-all"
            disabled={isLoading}
          />
        </div>

        {/* Search History */}
        {searchHistory.length > 0 && !isLoading && (
          <div className="flex gap-2 flex-wrap">
            <span className="text-xs text-gray-500">Recent:</span>
            {searchHistory.slice(0, 3).map((term, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleHistoryClick(term)}
                className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-sm text-gray-300 transition-colors"
              >
                {term}
              </button>
            ))}
          </div>
        )}

        {/* Threshold Slider */}
        <div className="flex items-center space-x-4">
          <label className="text-sm text-gray-300 font-medium whitespace-nowrap">
            Similarity: <span className="text-blue-400">{(threshold * 100).toFixed(0)}%</span>
          </label>
          <input
            type="range"
            min="0.2"
            max="0.9"
            step="0.1"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
            disabled={isLoading}
          />
        </div>

        {/* Search Button */}
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 
                   disabled:cursor-not-allowed text-white font-semibold py-3 px-6 
                   rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              Search Code
            </>
          )}
        </button>
      </form>
    </div>
  );
};
