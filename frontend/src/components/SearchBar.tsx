import React, { useState } from "react";
import { Search } from "lucide-react";

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
            placeholder="Search your codebase... (e.g., multiply, string operations)"
            className="w-full pl-12 pr-4 py-4 bg-slate-800 border border-slate-700 rounded-lg 
                     text-white placeholder-gray-400 focus:outline-none focus:ring-2 
                     focus:ring-primary focus:border-transparent text-lg"
            disabled={isLoading}
          />
        </div>

        {/* Threshold Slider */}
        <div className="flex items-center space-x-4">
          <label className="text-sm text-gray-300 font-medium">
            Similarity Threshold:
          </label>
          <input
            type="range"
            min="0.1"
            max="0.9"
            step="0.1"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            disabled={isLoading}
          />
          <span className="text-sm font-mono bg-slate-800 px-3 py-1 rounded">
            {threshold.toFixed(1)}
          </span>
        </div>

        {/* Search Button */}
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="w-full bg-primary hover:bg-blue-600 disabled:bg-slate-700 
                   disabled:cursor-not-allowed text-white font-semibold py-3 px-6 
                   rounded-lg transition-colors duration-200"
        >
          {isLoading ? "Searching..." : "Search Code"}
        </button>
      </form>
    </div>
  );
};
