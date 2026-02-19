import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Github, FileCode, TrendingUp, Shield, Search, Network, Sparkles, BarChart2 } from 'lucide-react';
import { repositoryApi } from '../services/repositoryApi';
import { Repository } from '../types/repository';
import { FilesTab } from '../components/FilesTab';
import { QualityTab } from '../components/QualityTab';
import { SecurityTab } from '../components/SecurityTab';
import CallGraphTab from '../components/CallGraphTab';
import { AiAssistantTab } from '../components/AiAssistantTab';

export default function RepositoryDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const [repository, setRepository] = useState<Repository | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'files' | 'quality' | 'security' | 'search' | 'callgraph' | 'ai'>('files');

  useEffect(() => {
    if (id) {
      loadRepository();
    }
  }, [id]);

  const loadRepository = async () => {
    if (!id) return;
    try {
      const data = await repositoryApi.getById(id);
      setRepository(data);
    } catch (error) {
      console.error('Failed to load repository:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400">Loading repository...</p>
        </div>
      </div>
    );
  }

  if (!repository) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl font-semibold text-slate-900 dark:text-white mb-4">
            Repository not found
          </p>
          <Link
            to="/repositories"
            className="text-blue-600 dark:text-blue-400 hover:underline"
          >
            Back to repositories
          </Link>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'files', label: 'Files', icon: FileCode },
    { id: 'quality', label: 'Quality', icon: TrendingUp },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'callgraph', label: 'Call Graph', icon: Network },
    { id: 'ai', label: 'AI Assistant', icon: Sparkles },
    { id: 'search', label: 'Search', icon: Search },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 p-8 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="p-4 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl">
                {repository.github_url ? (
                  <Github className="w-8 h-8 text-white" />
                ) : (
                  <FileCode className="w-8 h-8 text-white" />
                )}
              </div>
              <div>
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
                  {repository.name}
                </h1>
                <div className="flex gap-4">
                  {repository.github_url && (
                    <a
                      href={repository.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-2"
                    >
                      <Github className="w-4 h-4" />
                      View on GitHub
                    </a>
                  )}
                  {/* Sprint 9: Analysis Dashboard Button */}
                  <Link 
                    to={`/analysis/${id}`}
                    className="text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-2 font-semibold"
                  >
                    <BarChart2 className="w-4 h-4" />
                    Open Analysis Dashboard
                  </Link>
                </div>
              </div>
            </div>
            <span
              className={`px-4 py-2 rounded-full text-sm font-semibold ${
                repository.status === 'completed'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                  : repository.status === 'processing'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                  : repository.status === 'failed'
                  ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
              }`}
            >
              {repository.status}
            </span>
          </div>

          <div className="grid grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Files</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                {repository.file_count}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Symbols</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                {repository.symbol_count}
              </p>
            </div>
            {repository.github_stars !== undefined && (
              <div>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Stars</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  ⭐ {repository.github_stars}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
          <div className="border-b border-slate-200 dark:border-slate-700">
            <div className="flex gap-2 p-2 overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex-1 min-w-[140px] px-6 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="p-8">
            {activeTab === 'files' && <FilesTab />}
            {activeTab === 'quality' && <QualityTab />}
            {activeTab === 'security' && <SecurityTab />}
            {activeTab === 'callgraph' && id && <CallGraphTab repositoryId={id} />}
            {activeTab === 'ai' && <AiAssistantTab />}
            {activeTab === 'search' && (
              <div className="text-center py-12">
                <Search className="w-16 h-16 text-slate-400 mx-auto mb-4" />
                <p className="text-lg text-slate-600 dark:text-slate-400 mb-4">
                  Repository-specific search coming soon
                </p>
                <Link
                  to="/search"
                  className="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Use global search →
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
