import React, { useState, useEffect } from "react";
import { SearchBar } from "./components/SearchBar";
import { SearchResults } from "./components/SearchResult";
import { Stats } from "./components/Stats";
import { RepositoryUpload } from "./components/RepositoryUpload";
import { searchAPI, type SearchResponse } from "./services/api";
import {
  Code2,
  Upload as UploadIcon,
  Menu,
  X,
  AlertCircle,
} from "lucide-react";

function App() {
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number | undefined>(undefined);
  const [showUpload, setShowUpload] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [statsError, setStatsError] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/search/stats");
      if (!response.ok) {
        throw new Error("Failed to fetch stats");
      }
      const data = await response.json();
      setStats(data);
      setStatsError(false);
    } catch (err) {
      console.error("Failed to fetch stats", err);
      setStatsError(true);
      setStats({
        total_symbols: 0,
        total_embeddings: 0,
        coverage: 0,
        enabled: false,
      });
    }
  };

  const handleSearch = async (query: string, threshold: number) => {
    setIsLoading(true);
    setError(null);
    const startTime = performance.now();

    try {
      const results = await searchAPI.semanticSearch(query, threshold);
      const endTime = performance.now();
      setSearchResults(results);
      setSearchTime(Math.round(endTime - startTime));
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || "Search failed";
      setError(
        `${errorMessage}. Please check if the backend is running on port 8000.`,
      );
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    setShowUpload(false);
    setTimeout(() => {
      fetchStats();
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900">
      {statsError && (
        <div className="bg-red-500 text-white px-4 py-3 text-center text-sm font-medium">
          <AlertCircle className="w-4 h-4 inline mr-2" />
          Cannot connect to backend at http://localhost:8000 - Please ensure the
          backend is running
        </div>
      )}

      <header className="sticky top-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-lg border-b border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2.5 rounded-xl shadow-lg">
                <Code2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Code Intelligence
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
                  AI-Powered Search
                </p>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-6">
              {stats && !statsError && (
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-lg">
                    <span className="text-slate-600 dark:text-slate-400">
                      Symbols:
                    </span>
                    <span className="font-bold text-slate-900 dark:text-white">
                      {stats.total_symbols.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <span className="text-green-700 dark:text-green-400">
                      Coverage:
                    </span>
                    <span className="font-bold text-green-600 dark:text-green-400">
                      {stats.coverage}%
                    </span>
                  </div>
                </div>
              )}
              <button
                onClick={() => setShowUpload(!showUpload)}
                className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-semibold transition-all shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:-translate-y-0.5 flex items-center gap-2"
              >
                <UploadIcon className="w-4 h-4" />
                <span>Upload Code</span>
              </button>
            </div>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>

          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-slate-200 dark:border-slate-800 space-y-4">
              {stats && !statsError && (
                <div className="flex flex-col gap-2 text-sm">
                  <div className="flex justify-between items-center px-3 py-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
                    <span className="text-slate-600 dark:text-slate-400">
                      Symbols:
                    </span>
                    <span className="font-bold text-slate-900 dark:text-white">
                      {stats.total_symbols.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between items-center px-3 py-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <span className="text-green-700 dark:text-green-400">
                      Coverage:
                    </span>
                    <span className="font-bold text-green-600 dark:text-green-400">
                      {stats.coverage}%
                    </span>
                  </div>
                </div>
              )}
              <button
                onClick={() => {
                  setShowUpload(!showUpload);
                  setMobileMenuOpen(false);
                }}
                className="w-full px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold flex items-center justify-center gap-2"
              >
                <UploadIcon className="w-4 h-4" />
                Upload Code
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {showUpload && (
          <div className="mb-8 animate-fadeIn">
            <RepositoryUpload onUploadSuccess={handleUploadSuccess} />
          </div>
        )}

        <div className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {error && (
          <div className="mb-8 p-5 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-xl flex items-start gap-3 animate-fadeIn">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900 dark:text-red-100">
                Search Error
              </p>
              <p className="text-red-700 dark:text-red-300 text-sm mt-1">
                {error}
              </p>
            </div>
          </div>
        )}

        {searchResults && searchResults.total_results > 0 && (
          <div className="animate-fadeIn">
            <Stats
              totalResults={searchResults.total_results}
              searchTime={searchTime}
              threshold={searchResults.threshold}
            />
            <SearchResults
              results={searchResults.results}
              query={searchResults.query}
            />
          </div>
        )}

        {!searchResults && !error && !showUpload && (
          <div className="text-center py-20 animate-fadeIn">
            <div className="mb-8">
              <div className="inline-flex p-6 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl shadow-2xl shadow-blue-500/30">
                <Code2 className="w-20 h-20 text-white" />
              </div>
            </div>
            <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
              Search Your Codebase
            </h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg mb-8 max-w-2xl mx-auto leading-relaxed">
              Use natural language to find functions, classes, and patterns in
              your code.
              <br />
              Powered by AI embeddings for semantic understanding.
            </p>
            {stats && stats.total_symbols === 0 && !statsError && (
              <div className="space-y-4">
                <p className="text-slate-500 dark:text-slate-400 font-medium">
                  Get started by uploading your first repository
                </p>
                <button
                  onClick={() => setShowUpload(true)}
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-semibold text-lg shadow-2xl shadow-blue-500/30 hover:shadow-blue-500/50 transition-all hover:-translate-y-1 inline-flex items-center gap-3"
                >
                  <UploadIcon className="w-6 h-6" />
                  Upload Your First Repository
                </button>
              </div>
            )}
          </div>
        )}

        {searchResults && searchResults.total_results === 0 && (
          <div className="text-center py-16 bg-slate-100 dark:bg-slate-800/50 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 animate-fadeIn">
            <div className="mb-4">
              <Code2 className="w-16 h-16 text-slate-400 dark:text-slate-600 mx-auto" />
            </div>
            <p className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              No results found
            </p>
            <p className="text-slate-600 dark:text-slate-400">
              Try lowering the similarity threshold or using different keywords
            </p>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-200 dark:border-slate-800 mt-20 py-8 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-slate-600 dark:text-slate-400 text-sm">
            Powered by <span className="font-semibold">OpenAI Embeddings</span>{" "}
            • <span className="font-semibold">FastAPI</span> •{" "}
            <span className="font-semibold">PostgreSQL</span> •{" "}
            <span className="font-semibold">React</span>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
