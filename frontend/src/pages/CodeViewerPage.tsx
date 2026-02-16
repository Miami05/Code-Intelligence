import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FileCode, Copy, Check, ChevronRight, Code2, AlertCircle } from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cobol';
import { repositoryApi } from '../services/repositoryApi';
import { RepositorySymbol, FileContent } from '../types/repository';

export default function CodeViewerPage() {
  const { id } = useParams<{ id: string }>();
  const filePath = decodeURIComponent(window.location.pathname.split('/files/')[1] || '');
  
  const [fileData, setFileData] = useState<FileContent | null>(null);
  const [symbols, setSymbols] = useState<RepositorySymbol[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [highlightedLine, setHighlightedLine] = useState<number | null>(null);

  useEffect(() => {
    if (id && filePath) {
      loadFileData();
    }
  }, [id, filePath]);

  useEffect(() => {
    if (fileData?.content) {
      Prism.highlightAll();
    }
  }, [fileData]);

  const loadFileData = async () => {
    if (!id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Load file content and symbols in parallel
      const [contentData, symbolsData] = await Promise.all([
        repositoryApi.getFileContent(id, filePath),
        repositoryApi.getSymbols(id),
      ]);
      
      setFileData(contentData);
      
      // Filter symbols for this file
      const fileSymbols = symbolsData.symbols.filter(
        (s: RepositorySymbol) => s.file_path === filePath
      );
      setSymbols(fileSymbols);
    } catch (err: any) {
      console.error('Failed to load file data:', err);
      setError(err.response?.data?.detail || 'Failed to load file content');
    } finally {
      setLoading(false);
    }
  };

  const getLanguage = (lang: string): string => {
    const langMap: Record<string, string> = {
      'Python': 'python',
      'C': 'c',
      'COBOL': 'cobol',
      'Assembly': 'asm',
    };
    return langMap[lang] || 'javascript';
  };

  const copyToClipboard = () => {
    if (fileData?.content) {
      navigator.clipboard.writeText(fileData.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const jumpToLine = (lineNumber: number) => {
    setHighlightedLine(lineNumber);
    const lineElement = document.getElementById(`line-${lineNumber}`);
    if (lineElement) {
      lineElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400">Loading file...</p>
        </div>
      </div>
    );
  }

  if (error || !fileData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            Failed to Load File
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mb-6">
            {error || 'File not found'}
          </p>
          <Link
            to={`/repositories/${id}`}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all inline-block"
          >
            Back to Repository
          </Link>
        </div>
      </div>
    );
  }

  const language = getLanguage(fileData.language);
  const lines = fileData.content.split('\n');
  const pathParts = filePath.split('/');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm flex-wrap">
            <Link
              to={`/repositories/${id}`}
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Repository
            </Link>
            <ChevronRight className="w-4 h-4 text-slate-400" />
            {pathParts.map((part, index) => (
              <span key={index} className="flex items-center gap-2">
                {index > 0 && <ChevronRight className="w-4 h-4 text-slate-400" />}
                <span
                  className={index === pathParts.length - 1 ? 'font-semibold text-slate-900 dark:text-white' : 'text-slate-600 dark:text-slate-400'}
                >
                  {part}
                </span>
              </span>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Symbols Sidebar */}
          {symbols.length > 0 && (
            <div className="lg:col-span-1">
              <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 p-6 sticky top-24">
                <h3 className="font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                  <Code2 className="w-5 h-5" />
                  Symbols ({symbols.length})
                </h3>
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {symbols.map((symbol) => (
                    <button
                      key={symbol.symbol_id}
                      onClick={() => jumpToLine(symbol.line_start)}
                      className="w-full text-left p-3 bg-slate-50 dark:bg-slate-900 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="font-mono font-semibold text-sm text-slate-900 dark:text-white truncate">
                            {symbol.name}
                          </p>
                          <p className="text-xs text-slate-600 dark:text-slate-400 capitalize">
                            {symbol.type}
                          </p>
                        </div>
                        <span className="text-xs text-blue-600 dark:text-blue-400 ml-2">
                          L{symbol.line_start}
                        </span>
                      </div>
                      {symbol.cyclomatic_complexity && (
                        <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
                          Complexity: {symbol.cyclomatic_complexity}
                        </p>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Code Content */}
          <div className={symbols.length > 0 ? 'lg:col-span-3' : 'lg:col-span-4'}>
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
                <div className="flex items-center gap-3">
                  <FileCode className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  <div>
                    <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                      {pathParts[pathParts.length - 1]}
                    </h2>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      {lines.length} lines • {fileData.language} • {(fileData.size_bytes / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                <button
                  onClick={copyToClipboard}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all flex items-center gap-2"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy
                    </>
                  )}
                </button>
              </div>

              {/* Code Content */}
              <div className="bg-slate-900 overflow-x-auto">
                <pre className="!bg-slate-900 !m-0 !p-0">
                  <code className={`language-${language} !bg-slate-900`}>
                    {lines.map((line, index) => {
                      const lineNumber = index + 1;
                      const isHighlighted = highlightedLine === lineNumber;
                      return (
                        <div
                          key={lineNumber}
                          id={`line-${lineNumber}`}
                          className={`flex ${
                            isHighlighted ? 'bg-yellow-900/30' : ''
                          }`}
                        >
                          <span className="inline-block w-16 text-right pr-4 py-1 text-slate-500 select-none border-r border-slate-700 flex-shrink-0">
                            {lineNumber}
                          </span>
                          <span className="pl-4 py-1 flex-1 min-w-0">{line || ' '}</span>
                        </div>
                      );
                    })}
                  </code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
