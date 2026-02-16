import { useState } from 'react';
import { Search } from 'lucide-react';
import { SearchBar } from '../components/SearchBar';
import { SearchResults } from '../components/SearchResult';
import { Stats } from '../components/Stats';
import { searchAPI, type SearchResponse } from '../services/api';
import { Language } from '../types/api';

export default function SearchPage() {
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number | undefined>(undefined);

  const handleSearch = async (query: string, threshold: number, language?: Language) => {
    setIsLoading(true);
    setError(null);
    const startTime = performance.now();

    try {
      const results = await searchAPI.semanticSearch({ query, threshold, language });
      const endTime = performance.now();
      setSearchResults(results);
      setSearchTime(Math.round(endTime - startTime));
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Search failed';
      setError(`${errorMessage}. Please check if the backend is running on port 8000.`);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <div className="inline-flex p-6 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl shadow-2xl shadow-blue-500/30 mb-6">
            <Search className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
            Semantic Code Search
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Search your codebase using natural language powered by AI embeddings
          </p>
        </div>

        <div className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {error && (
          <div className="mb-8 p-5 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-xl">
            <p className="text-red-900 dark:text-red-100 font-semibold">Error</p>
            <p className="text-red-700 dark:text-red-300 text-sm mt-1">{error}</p>
          </div>
        )}

        {searchResults && searchResults.total_results > 0 && (
          <div>
            <Stats
              totalResults={searchResults.total_results}
              searchTime={searchTime}
              threshold={searchResults.threshold}
            />
            <SearchResults results={searchResults.results} query={searchResults.query} />
          </div>
        )}

        {searchResults && searchResults.total_results === 0 && (
          <div className="text-center py-16 bg-white dark:bg-slate-800 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700">
            <Search className="w-16 h-16 text-slate-400 mx-auto mb-4" />
            <p className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              No results found
            </p>
            <p className="text-slate-600 dark:text-slate-400">
              Try lowering the similarity threshold or using different keywords
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
