import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Github, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { githubApi } from '../services/githubApi';
import { GitHubImportRequest } from '../types/github';

export default function GitHubImportPage() {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [token, setToken] = useState('');
  const [validating, setValidating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [validation, setValidation] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const validateURL = async () => {
    if (!url) return;
    
    setValidating(true);
    setError(null);
    setValidation(null);

    try {
      const result = await githubApi.validateURL(url);
      setValidation(result);
      if (result.branch) {
        setBranch(result.branch);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid GitHub URL');
    } finally {
      setValidating(false);
    }
  };

  const handleImport = async () => {
    if (!validation || !validation.valid) {
      setError('Please validate the URL first');
      return;
    }

    setImporting(true);
    setError(null);

    try {
      const request: GitHubImportRequest = {
        url,
        branch,
        token: token || undefined,
      };

      const response = await githubApi.importRepository(request);
      setSuccess(true);
      
      // Redirect to repository details after 2 seconds
      setTimeout(() => {
        navigate(`/repositories/${response.repository_id}`);
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import repository');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 py-12">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 p-8">
          <div className="flex items-center gap-4 mb-8">
            <div className="p-4 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl">
              <Github className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                Import from GitHub
              </h1>
              <p className="text-slate-600 dark:text-slate-400">
                Import a repository for analysis
              </p>
            </div>
          </div>

          {success ? (
            <div className="text-center py-12">
              <div className="inline-flex p-6 bg-green-100 dark:bg-green-900/20 rounded-full mb-6">
                <CheckCircle2 className="w-16 h-16 text-green-600 dark:text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                Import Started!
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                Your repository is being processed in the background.
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-500">
                Redirecting to repository details...
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* URL Input */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  GitHub Repository URL *
                </label>
                <div className="flex gap-2">
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => {
                      setUrl(e.target.value);
                      setValidation(null);
                      setError(null);
                    }}
                    placeholder="https://github.com/owner/repository"
                    className="flex-1 px-4 py-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={validateURL}
                    disabled={!url || validating}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {validating ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      'Validate'
                    )}
                  </button>
                </div>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  Example: https://github.com/facebook/react
                </p>
              </div>

              {/* Validation Result */}
              {validation && validation.valid && (
                <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
                  <div>
                    <p className="font-semibold text-green-900 dark:text-green-100">
                      Valid Repository
                    </p>
                    <p className="text-sm text-green-700 dark:text-green-300">
                      {validation.owner}/{validation.repo}
                    </p>
                  </div>
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
                  <div>
                    <p className="font-semibold text-red-900 dark:text-red-100">Error</p>
                    <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                  </div>
                </div>
              )}

              {/* Branch Input */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  Branch
                </label>
                <input
                  type="text"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  placeholder="main"
                  className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Token Input */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  Personal Access Token (Optional)
                </label>
                <input
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                  className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  Required for private repositories
                </p>
              </div>

              {/* Import Button */}
              <button
                onClick={handleImport}
                disabled={!validation || !validation.valid || importing}
                className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-semibold text-lg shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
              >
                {importing ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    <Github className="w-6 h-6" />
                    Import Repository
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
