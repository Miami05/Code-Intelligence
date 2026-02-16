import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Code2, Upload, Github, Search, TrendingUp, Shield } from 'lucide-react';
import { githubApi } from '../services/githubApi';
import { repositoryApi } from '../services/repositoryApi';
import { GitHubStats } from '../types/github';

export default function HomePage() {
  const [stats, setStats] = useState<GitHubStats | null>(null);
  const [allStats, setAllStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [githubStats, repoList] = await Promise.all([
        githubApi.getStats(),
        repositoryApi.listAll(10, 0),
      ]);
      setStats(githubStats);
      setAllStats(repoList);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <div className="mb-8">
            <div className="inline-flex p-6 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl shadow-2xl shadow-blue-500/30">
              <Code2 className="w-20 h-20 text-white" />
            </div>
          </div>
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">
            Code Intelligence Platform
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 mb-8 max-w-3xl mx-auto leading-relaxed">
            AI-powered code analysis platform that understands your codebase.
            Import from GitHub, analyze quality, detect security issues, and search semantically.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              to="/repositories/import"
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-semibold text-lg shadow-2xl shadow-blue-500/30 hover:shadow-blue-500/50 transition-all hover:-translate-y-1 inline-flex items-center gap-3"
            >
              <Github className="w-6 h-6" />
              Import from GitHub
            </Link>
            <Link
              to="/search"
              className="px-8 py-4 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-900 dark:text-white rounded-xl font-semibold text-lg shadow-xl border-2 border-slate-200 dark:border-slate-700 transition-all hover:-translate-y-1 inline-flex items-center gap-3"
            >
              <Search className="w-6 h-6" />
              Search Code
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        {!loading && stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-xl">
                  <Github className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Repositories</p>
                  <p className="text-3xl font-bold text-slate-900 dark:text-white">
                    {stats.total_repositories}
                  </p>
                </div>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                {stats.completed} completed, {stats.processing} processing
              </p>
            </div>

            <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-xl">
                  <Code2 className="w-8 h-8 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Symbols</p>
                  <p className="text-3xl font-bold text-slate-900 dark:text-white">
                    {stats.total_symbols.toLocaleString()}
                  </p>
                </div>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Functions, classes analyzed
              </p>
            </div>

            <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-xl">
                  <TrendingUp className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Files</p>
                  <p className="text-3xl font-bold text-slate-900 dark:text-white">
                    {stats.total_files.toLocaleString()}
                  </p>
                </div>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Across all repositories
              </p>
            </div>
          </div>
        )}

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
            <div className="p-4 bg-blue-100 dark:bg-blue-900/20 rounded-xl inline-block mb-4">
              <Github className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
              GitHub Integration
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              Import repositories directly from GitHub with automatic analysis and metadata extraction.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
            <div className="p-4 bg-green-100 dark:bg-green-900/20 rounded-xl inline-block mb-4">
              <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
              Quality Analysis
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              Automatic code complexity, maintainability metrics, and quality recommendations.
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
            <div className="p-4 bg-purple-100 dark:bg-purple-900/20 rounded-xl inline-block mb-4">
              <Shield className="w-8 h-8 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
              Security Detection
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              Identify potential security vulnerabilities and code smells automatically.
            </p>
          </div>
        </div>

        {/* Recent Repositories */}
        {allStats && allStats.repositories && allStats.repositories.length > 0 && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
                Recent Repositories
              </h2>
              <Link
                to="/repositories"
                className="text-blue-600 dark:text-blue-400 hover:underline font-semibold"
              >
                View all →
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {allStats.repositories.slice(0, 4).map((repo: any) => (
                <Link
                  key={repo.id}
                  to={`/repositories/${repo.id}`}
                  className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 hover:shadow-xl transition-all hover:-translate-y-1"
                >
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                    {repo.name}
                  </h3>
                  <div className="flex gap-4 text-sm text-slate-600 dark:text-slate-400">
                    <span>{repo.file_count} files</span>
                    <span>{repo.symbol_count} symbols</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
