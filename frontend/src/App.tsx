import React, { useState } from "react";
import { SearchBar } from "./components/SearchBar";
import { SearchResults } from "./components/SearchResults";
import { Stats } from "./components/Stats";
import { searchAPI, SearchResponse } from "./services/api";
import { Code2, Sparkles } from "lucide-react";

function App() {
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number | undefined>(undefined);

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
      setError(
        "Failed to search. Make sure the backend is running on http://localhost:8000",
      );
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center space-x-3">
            <Code2 className="w-8 h-8 text-primary" />
            <h1 className="text-3xl font-bold text-white">Code Intelligence</h1>
            <Sparkles className="w-6 h-6 text-yellow-400" />
          </div>
          <p className="text-gray-400 mt-2">
            Semantic code search powered by AI embeddings
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-8">
            {error}
          </div>
        )}

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

        {!searchResults && !error && (
          <div className="text-center py-20">
            <Code2 className="w-20 h-20 text-gray-700 mx-auto mb-6" />
            <h2 className="text-2xl font-semibold text-gray-300 mb-2">
              Start Your Search
            </h2>
            <p className="text-gray-500">
              Search for functions, classes, or any code concept using natural
              language
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700 mt-20">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center text-gray-500 text-sm">
          Built with React + FastAPI + PostgreSQL + Sentence Transformers 🚀
        </div>
      </footer>
    </div>
  );
}

export default App;
