import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter } from 'lucide-react';
import { repositoryApi } from '../services/repositoryApi';
import { Repository } from '../types/repository';

export default function RepositoriesPage() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState<'all' | 'github' | 'upload'>('all');

  useEffect(() => {
    loadRepositories();
  }, []);

  const loadRepositories = async () => {
    try {
      // Fixed: Changed from listAll() to list() - correct method name
      const data = await repositoryApi.list(100, 0);
      setRepositories(data.repositories);
    } catch (error) {
      console.error('Failed to load repositories:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRepos = repositories.filter((repo) => {
    const matchesSearch = repo.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSource =
      sourceFilter === 'all' ||
      (sourceFilter === 'github' && repo.github_url) ||
      (sourceFilter === 'upload' && !repo.github_url);
    return matchesSearch && matchesSource;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2">
              Repositories
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              {filteredRepos.length} repositories found
            </p>
          </div>
          <Link
            to="/import"
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-semibold shadow-lg transition-all hover:-translate-y-1 inline-flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Import Repository
          </Link>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search repositories..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex gap-2">
            {['all', 'github', 'upload'].map((filter) => (
              <button
                key={filter}
                onClick={() => setSourceFilter(filter as any)}
                className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                  sourceFilter === filter
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'
                }`}
              >
                {filter.charAt(0).toUpperCase() + filter.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Repository Grid */}
        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-slate-600 dark:text-slate-400">Loading repositories...</p>
          </div>
        ) : filteredRepos.length === 0 ? (
          <div className="text-center py-20 bg-white dark:bg-slate-800 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700">
            <p className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              No repositories found
            </p>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              {searchQuery ? 'Try a different search term' : 'Import your first repository'}
            </p>
            <Link
              to="/import"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold transition-all"
            >
              <Plus className="w-5 h-5" />
              Import Repository
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRepos.map((repo) => (
              <Link
                key={repo.id}
                to={`/repositories/${repo.id}`}
                className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 hover:shadow-xl transition-all hover:-translate-y-1"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                    {repo.name}
                  </h3>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      repo.status === 'completed'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : repo.status === 'processing'
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                        : repo.status === 'failed'
                        ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                    }`}
                  >
                    {repo.status}
                  </span>
                </div>
                {repo.github_language && (
                  <div className="mb-3">
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400 text-xs font-medium rounded">
                      {repo.github_language}
                    </span>
                  </div>
                )}
                <div className="flex gap-4 text-sm text-slate-600 dark:text-slate-400">
                  <span>{repo.file_count} files</span>
                  <span>{repo.symbol_count} symbols</span>
                  {repo.github_stars && <span>⭐ {repo.github_stars}</span>}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
