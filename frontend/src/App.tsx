import { useState, useEffect } from "react";
import { SearchBar } from "./components/SearchBar";
import { SearchResults } from "./components/SearchResult";
import { Stats } from "./components/Stats";
import { RepositoryUpload } from "./components/RepositoryUpload";
import { searchAPI, type SearchResponse } from "./services/api";
import {
  Code2,
  Upload as UploadIcon,
  Sparkles,
  Database,
  Zap,
  X,
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

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/search/stats");
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error("Failed to fetch stats", err);
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
    } catch (err: an) {
      const errorMessage =
        err.response?.data?.detail || err.message || "Search failed";
      setError(
        `⚠️ ${errorMessage}\n\nTroubleshooting:\n• Check if backend is running on port 8000\n• Verify database has embeddings\n• Try uploading a repository first`,
      );
      console.error("Search error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    setShowUpload(false);
    fetchStats();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-slate-900 dark:to-blue-950">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-blue-400/10 to-purple-400/10 dark:from-blue-600/5 dark:to-purple-600/5 rounded-full blur-3xl animate-pulse"></div>
        <div
          className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-indigo-400/10 to-pink-400/10 dark:from-indigo-600/5 dark:to-pink-600/5 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: "1s" }}
        ></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="backdrop-blur-xl bg-white/70 dark:bg-gray-900/70 border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50 shadow-lg shadow-black/5">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-20">
              {/* Logo */}
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl blur-lg opacity-50 animate-pulse"></div>
                  <div className="relative bg-gradient-to-br from-blue-600 to-purple-600 p-3 rounded-2xl shadow-xl">
                    <Code2 className="w-7 h-7 text-white" />
                  </div>
                </div>
                <div>
                  <h1 className="text-2xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    CodeSearch AI
                  </h1>
                  <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">
                    Semantic Code Intelligence
                  </p>
                </div>
              </div>

              {/* Stats & Actions */}
              <div className="flex items-center gap-4">
                {stats && (
                  <div className="hidden md:flex items-center gap-6 px-6 py-3 bg-white/80 dark:bg-gray-800/80 rounded-2xl border border-gray-200/50 dark:border-gray-700/50 shadow-lg">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      <div>
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">
                          {stats.total_symbols.toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          symbols
                        </p>
                      </div>
                    </div>
                    <div className="h-10 w-px bg-gray-300 dark:bg-gray-600"></div>
                    <div className="flex items-center gap-2">
                      <Zap className="w-4 h-4 text-green-600 dark:text-green-400" />
                      <div>
                        <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {stats.coverage}%
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          coverage
                        </p>
                      </div>
                    </div>
                  </div>
                )}
                <button
                  onClick={() => setShowUpload(!showUpload)}
                  className="relative group px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-2xl font-bold transition-all shadow-xl shadow-blue-500/25 hover:shadow-2xl hover:shadow-blue-500/40 hover:scale-105 flex items-center gap-2"
                >
                  <UploadIcon className="w-5 h-5" />
                  <span className="hidden sm:inline">Upload Code</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Upload Section */}
          {showUpload && (
            <div className="mb-12 animate-fadeIn">
              <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Upload Repository
                  </h2>
                  <button
                    onClick={() => setShowUpload(false)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
                  >
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>
                <RepositoryUpload onUploadSuccess={handleUploadSuccess} />
              </div>
            </div>
          )}

          {/* Search Section */}
          <div className="mb-12">
            <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 p-8">
              <SearchBar onSearch={handleSearch} isLoading={isLoading} />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-12 animate-fadeIn">
              <div className="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border-2 border-red-300 dark:border-red-700 rounded-3xl p-8 shadow-xl">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-red-500 rounded-2xl flex items-center justify-center">
                    <span className="text-2xl">⚠️</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-red-900 dark:text-red-100 mb-2">
                      Search Error
                    </h3>
                    <pre className="text-sm text-red-800 dark:text-red-200 whitespace-pre-wrap font-medium">
                      {error}
                    </pre>
                  </div>
                  <button
                    onClick={() => setError(null)}
                    className="flex-shrink-0 p-2 hover:bg-red-100 dark:hover:bg-red-800/50 rounded-xl transition-colors"
                  >
                    <X className="w-5 h-5 text-red-600 dark:text-red-400" />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Search Results */}
          {searchResults && searchResults.total_results > 0 && (
            <div className="space-y-8 animate-fadeIn">
              <Stats
                totalResults={searchResults.total_results}
                searchTime={searchTime}
                threshold={searchResults.threshold}
              />
              <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 p-8">
                <SearchResults
                  results={searchResults.results}
                  query={searchResults.query}
                />
              </div>
            </div>
          )}

          {/* No Results */}
          {searchResults && searchResults.total_results === 0 && !error && (
            <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 p-16 text-center animate-fadeIn">
              <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 rounded-3xl flex items-center justify-center">
                <span className="text-5xl">🔍</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                No results found
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Try adjusting your search query or lowering the similarity
                threshold
              </p>
            </div>
          )}

          {/* Empty State */}
          {!searchResults && !error && !showUpload && (
            <div className="text-center py-20 animate-fadeIn">
              <div className="mb-10">
                <div className="relative inline-block">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl blur-2xl opacity-30 animate-pulse"></div>
                  <div className="relative inline-flex p-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl shadow-2xl">
                    <Sparkles className="w-20 h-20 text-white" />
                  </div>
                </div>
              </div>
              <h2 className="text-5xl font-black bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
                AI-Powered Code Search
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-400 mb-4 max-w-3xl mx-auto leading-relaxed">
                Search your codebase using natural language. Our AI understands
                context, meaning, and relationships between code elements.
              </p>
              <p className="text-lg text-gray-500 dark:text-gray-500 mb-12 max-w-2xl mx-auto">
                Find functions, classes, and patterns instantly with semantic
                understanding
              </p>

              {/* Features */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto mb-12">
                <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-xl">
                  <div className="w-14 h-14 bg-blue-100 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Sparkles className="w-7 h-7 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                    Semantic Search
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    AI understands meaning, not just keywords
                  </p>
                </div>
                <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-xl">
                  <div className="w-14 h-14 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Zap className="w-7 h-7 text-purple-600 dark:text-purple-400" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                    Lightning Fast
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Vector similarity search in milliseconds
                  </p>
                </div>
                <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 shadow-xl">
                  <div className="w-14 h-14 bg-green-100 dark:bg-green-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Database className="w-7 h-7 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                    Smart Indexing
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Automatic code analysis and embedding
                  </p>
                </div>
              </div>

              {stats && stats.total_symbols === 0 && (
                <button
                  onClick={() => setShowUpload(true)}
                  className="group relative px-10 py-5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-2xl font-bold text-xl shadow-2xl shadow-blue-500/25 hover:shadow-3xl hover:shadow-blue-500/40 transition-all hover:scale-105 inline-flex items-center gap-4"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity"></div>
                  <UploadIcon className="w-7 h-7 relative z-10" />
                  <span className="relative z-10">
                    Upload Your First Repository
                  </span>
                </button>
              )}
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-200/50 dark:border-gray-700/50 mt-20 py-12 backdrop-blur-xl bg-white/50 dark:bg-gray-900/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                  <Code2 className="w-5 h-5 text-white" />
                </div>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  CodeSearch AI
                </p>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Powered by{" "}
                <span className="font-semibold">OpenAI Embeddings</span> •
                <span className="font-semibold"> FastAPI</span> •
                <span className="font-semibold"> PostgreSQL</span> •
                <span className="font-semibold"> React</span>
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
