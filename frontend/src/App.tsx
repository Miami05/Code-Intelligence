import { useState, useEffect } from "react";
import { SearchBar } from "./components/SearchBar";
import { SearchResults } from "./components/SearchResult";
import { Stats } from "./components/Stats";
import { RepositoryUpload } from "./components/RepositoryUpload";
import { searchAPI, type SearchResponse } from "./services/api";
import { Code2, Upload as UploadIcon, Menu, X } from "lucide-react";

function App() {
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number | undefined>(undefined);
  const [showUpload, setShowUpload] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
    } catch (err) {
      setError("Search failed. Please check if the backend is running.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    setShowUpload(false);
    fetchStats();
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950">
      {/* Modern Header */}
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-xl">
                <Code2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Code Intelligence</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block">AI-Powered Search</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-4">
              {stats && (
                <div className="flex items-center gap-4 text-sm">
                  <div className="text-gray-600 dark:text-gray-300">
                    <span className="font-semibold text-gray-900 dark:text-white">{stats.total_symbols.toLocaleString()}</span> symbols
                  </div>
                  <div className="text-gray-600 dark:text-gray-300">
                    <span className="font-semibold text-green-600 dark:text-green-400">{stats.coverage}%</span> coverage
                  </div>
                </div>
              )}
              <button
                onClick={() => setShowUpload(!showUpload)}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-medium transition-all shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/40 flex items-center gap-2"
              >
                <UploadIcon className="w-4 h-4" />
                <span>Upload</span>
              </button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-200 dark:border-gray-800">
              {stats && (
                <div className="flex flex-col gap-2 mb-4 text-sm">
                  <div className="text-gray-600 dark:text-gray-300">
                    Symbols: <span className="font-semibold text-gray-900 dark:text-white">{stats.total_symbols.toLocaleString()}</span>
                  </div>
                  <div className="text-gray-600 dark:text-gray-300">
                    Coverage: <span className="font-semibold text-green-600 dark:text-green-400">{stats.coverage}%</span>
                  </div>
                </div>
              )}
              <button
                onClick={() => {
                  setShowUpload(!showUpload);
                  setMobileMenuOpen(false);
                }}
                className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium"
              >
                <UploadIcon className="w-4 h-4 inline mr-2" />
                Upload Code
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        {showUpload && (
          <div className="mb-8">
            <RepositoryUpload onUploadSuccess={handleUploadSuccess} />
          </div>
        )}

        {/* Search Section */}
        <div className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
            <p className="text-red-800 dark:text-red-200 font-medium">{error}</p>
          </div>
        )}

        {/* Search Results */}
        {searchResults && searchResults.total_results > 0 && (
          <>
            <Stats
              totalResults={searchResults.total_results}
              searchTime={searchTime}
              threshold={searchResults.threshold}
            />
            <SearchResults
              results={searchResults.results}
              query={searchResults.query}
            />
          </>
        )}

        {/* Empty State */}
        {!searchResults && !error && !showUpload && (
          <div className="text-center py-20">
            <div className="mb-8">
              <div className="inline-flex p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-xl shadow-blue-500/25">
                <Code2 className="w-16 h-16 text-white" />
              </div>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Search Your Codebase
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
              Use natural language to find functions, classes, and patterns in your code. Powered by AI embeddings for semantic understanding.
            </p>
            {stats && stats.total_symbols === 0 && (
              <button
                onClick={() => setShowUpload(true)}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-semibold text-lg shadow-xl shadow-blue-500/25 hover:shadow-2xl hover:shadow-blue-500/40 transition-all inline-flex items-center gap-3"
              >
                <UploadIcon className="w-6 h-6" />
                Upload Your First Repository
              </button>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 mt-20 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            Powered by OpenAI Embeddings • FastAPI • PostgreSQL • React
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
