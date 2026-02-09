import React, { useState } from "react";
import { Search, Loader2, Sparkles, ChevronDown } from "lucide-react";
import { Language } from "../types/api";
import { ALL_LANGUAGES } from "../config/languages";

interface SearchBarProps {
  onSearch: (query: string, threshold: number, language?: Language) => void;
  isLoading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  isLoading,
}) => {
  const [query, setQuery] = useState("");
  const [threshold, setThreshold] = useState(0.4);
  const [selectedLanguage, setSelectedLanguage] = useState<
    Language | undefined
  >();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, threshold, selectedLanguage);
    }
  };

  const selectedConfig = selectedLanguage
    ? ALL_LANGUAGES.find((l) => l.value === selectedLanguage)
    : null;

  const exampleQueries = [
    "functions that handle authentication",
    "database connection setup",
    "calculate totals",
    "parse JSON data",
  ];

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Main Search Input with Language Filter */}
        <div className="flex flex-col md:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
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

          {/* Language Filter Dropdown */}
          <div className="relative min-w-[180px]">
            <button
              type="button"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="w-full px-4 py-5 rounded-2xl border-2 border-gray-200 dark:border-gray-700
                       hover:border-gray-300 dark:hover:border-gray-600 focus:border-blue-500 dark:focus:border-blue-500 
                       focus:outline-none focus:ring-4 focus:ring-blue-500/10
                       flex items-center justify-between gap-2 bg-white dark:bg-gray-900
                       disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed
                       transition-all shadow-sm hover:shadow-md"
              disabled={isLoading}
            >
              <span className="flex items-center gap-2 truncate">
                {selectedConfig ? (
                  <>
                    <span className="text-xl">{selectedConfig.icon}</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {selectedConfig.label}
                    </span>
                  </>
                ) : (
                  <span className="text-gray-600 dark:text-gray-400">
                    All Languages
                  </span>
                )}
              </span>
              <ChevronDown
                className={`w-5 h-5 text-gray-500 transition-transform ${
                  isDropdownOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setIsDropdownOpen(false)}
                />
                <div
                  className="absolute top-full mt-2 w-full bg-white dark:bg-gray-900 rounded-xl shadow-2xl 
                              border-2 border-gray-200 dark:border-gray-700 z-20 overflow-hidden"
                >
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedLanguage(undefined);
                      setIsDropdownOpen(false);
                    }}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-800
                             transition-colors flex items-center gap-2 border-b border-gray-100 dark:border-gray-800
                             ${!selectedLanguage ? "bg-blue-50 dark:bg-blue-900/20 font-medium" : ""}`}
                  >
                    <span className="text-gray-700 dark:text-gray-300">
                      🌐 All Languages
                    </span>
                  </button>
                  {ALL_LANGUAGES.map((lang) => (
                    <button
                      key={lang.value}
                      type="button"
                      onClick={() => {
                        setSelectedLanguage(lang.value);
                        setIsDropdownOpen(false);
                      }}
                      className={`w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-800
                               transition-colors flex items-center gap-2
                               ${selectedLanguage === lang.value ? "bg-blue-50 dark:bg-blue-900/20 font-medium" : ""}`}
                    >
                      <span className="text-xl">{lang.icon}</span>
                      <span className="text-gray-900 dark:text-white">
                        {lang.label}
                      </span>
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Active Filter Display */}
        {selectedLanguage && (
          <div className="flex items-center gap-2 animate-fadeIn">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Filtering by:
            </span>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <span className="text-lg">{selectedConfig?.icon}</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {selectedConfig?.label}
              </span>
              <button
                type="button"
                onClick={() => setSelectedLanguage(undefined)}
                className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 ml-1"
              >
                ✕
              </button>
            </div>
          </div>
        )}

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
