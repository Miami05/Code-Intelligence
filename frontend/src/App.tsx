import { useState, useEffect } from "react";
import { SearchBar } from "./components/SearchBar";
import { SearchResults } from "./components/SearchResult";
import { Stats } from "./components/Stats";
import { RepositoryUpload } from "./components/RepositoryUpload";
import { searchAPI, type SearchResponse } from "./services/api";
import { Code2, Sparkles, Upload as UploadIcon, AlertCircle } from "lucide-react";

function App() {
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number | undefined>(undefined);
  const [showUpload, setShowUpload] = useState(false);
  const [stats, setStats] = useState<any>(null);

  // Fetch stats on mount
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
      
      if (results.total_results === 0) {
        setError("No results found. Try adjusting your search query or uploading more code.");
      }
    } catch (err) {
      setError(
        "Failed to search. Make sure the backend is running on http://localhost:8000",
      );
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Code2 className="w-8 h-8 text-blue-500" />
              <div>
                <h1 className="text-3xl font-bold text-white">Code Intelligence</h1>
                <p className="text-gray-400 text-sm mt-1">
                  Semantic code search powered by AI embeddings
                </p>
              </div>
              <Sparkles className="w-6 h-6 text-yellow-400" />
            </div>
            <button
              onClick={() => setShowUpload(!showUpload)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              <UploadIcon className="w-4 h-4" />
              Upload Code
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Stats Bar */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <p className="text-gray-400 text-sm">Total Symbols</p>
              <p className="text-2xl font-bold text-white mt-1">{stats.total_symbols.toLocaleString()}</p>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <p className="text-gray-400 text-sm">Embeddings</p>
              <p className="text-2xl font-bold text-white mt-1">{stats.total_embeddings.toLocaleString()}</p>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
              <p className="text-gray-400 text-sm">Coverage</p>
              <p className="text-2xl font-bold text-green-400 mt-1">{stats.coverage}%</p>
            </div>
          </div>
        )}

        {/* Upload Section */}
        {showUpload && (
          <RepositoryUpload onUploadSuccess={handleUploadSuccess} />
        )}

        {/* Search Bar */}
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/10 border border-red-500 rounded-lg p-4 mb-8">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-red-400">Search Failed</h3>
                <p className="text-sm text-red-300">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="text-sm text-red-400 underline mt-2 hover:text-red-300"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Search Results */}
        {searchResults && (
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
          <div className="text-center py-20 bg-slate-800/30 rounded-lg border border-slate-700">
            <Code2 className="w-20 h-20 text-gray-600 mx-auto mb-6" />
            <h2 className="text-2xl font-semibold text-gray-300 mb-2">
              Start Your Search
            </h2>
            <p className="text-gray-500 mb-6">
              Search for functions, classes, or any code concept using natural language
            </p>
            {stats && stats.total_symbols === 0 && (
              <button
                onClick={() => setShowUpload(true)}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium inline-flex items-center gap-2"
              >
                <UploadIcon className="w-5 h-5" />
                Upload Your First Repository
              </button>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700 mt-20">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center text-gray-500 text-sm">
          Built with React + FastAPI + PostgreSQL + OpenAI Embeddings 🚀
        </div>
      </footer>
    </div>
  );
}

export default App;
