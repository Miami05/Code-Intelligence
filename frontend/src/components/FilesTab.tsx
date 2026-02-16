import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { File, Folder, ChevronRight, ChevronDown, Code } from 'lucide-react';
import { repositoryApi } from '../services/repositoryApi';
import { RepositoryFile } from '../types/repository';

export function FilesTab() {
  const { id } = useParams<{ id: string }>();
  const [files, setFiles] = useState<RepositoryFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [languageFilter, setLanguageFilter] = useState<string>('');
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (id) {
      loadFiles();
    }
  }, [id, languageFilter]);

  const loadFiles = async () => {
    if (!id) return;
    try {
      const data = await repositoryApi.getFiles(id, languageFilter || undefined);
      setFiles(data.files);
    } catch (error) {
      console.error('Failed to load files:', error);
    } finally {
      setLoading(false);
    }
  };

  const languages = Array.from(new Set(files.map((f) => f.language))).sort();

  // Build file tree
  interface FileNode {
    name: string;
    path: string;
    isDirectory: boolean;
    children?: FileNode[];
    file?: RepositoryFile;
  }

  const buildFileTree = (files: RepositoryFile[]): FileNode[] => {
    const root: FileNode[] = [];
    const map = new Map<string, FileNode>();

    files.forEach((file) => {
      const parts = file.file_path.split('/');
      let currentPath = '';

      parts.forEach((part, index) => {
        const previousPath = currentPath;
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        const isLast = index === parts.length - 1;

        if (!map.has(currentPath)) {
          const node: FileNode = {
            name: part,
            path: currentPath,
            isDirectory: !isLast,
            children: isLast ? undefined : [],
            file: isLast ? file : undefined,
          };
          map.set(currentPath, node);

          if (previousPath) {
            const parent = map.get(previousPath);
            if (parent && parent.children) {
              parent.children.push(node);
            }
          } else {
            root.push(node);
          }
        }
      });
    });

    return root;
  };

  const toggleFolder = (path: string) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const renderTreeNode = (node: FileNode, level = 0) => {
    const isExpanded = expandedFolders.has(node.path);
    const paddingLeft = `${level * 1.5}rem`;

    return (
      <div key={node.path}>
        {node.isDirectory ? (
          <div>
            <button
              onClick={() => toggleFolder(node.path)}
              className="w-full flex items-center gap-2 px-4 py-2 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors text-left"
              style={{ paddingLeft }}
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 text-slate-500" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-500" />
              )}
              <Folder className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium text-slate-900 dark:text-white">
                {node.name}
              </span>
            </button>
            {isExpanded && node.children && (
              <div>{node.children.map((child) => renderTreeNode(child, level + 1))}</div>
            )}
          </div>
        ) : (
          <Link
            to={`/repositories/${id}/files/${node.path}`}
            className="w-full flex items-center gap-2 px-4 py-2 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
            style={{ paddingLeft }}
          >
            <File className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-700 dark:text-slate-300">{node.name}</span>
            <span className="ml-auto text-xs text-slate-500">
              {node.file?.line_count} lines
            </span>
          </Link>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-slate-600 dark:text-slate-400">Loading files...</p>
      </div>
    );
  }

  const fileTree = buildFileTree(files);

  return (
    <div>
      {/* Language Filter */}
      {languages.length > 1 && (
        <div className="mb-6">
          <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
            Filter by Language
          </label>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setLanguageFilter('')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                !languageFilter
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              All
            </button>
            {languages.map((lang) => (
              <button
                key={lang}
                onClick={() => setLanguageFilter(lang)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  languageFilter === lang
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                }`}
              >
                {lang}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* File Tree */}
      <div className="bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div className="p-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
          <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Code className="w-5 h-5" />
            Files ({files.length})
          </h3>
        </div>
        <div className="max-h-[600px] overflow-y-auto">
          {fileTree.length === 0 ? (
            <div className="text-center py-12">
              <File className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <p className="text-slate-600 dark:text-slate-400">No files found</p>
            </div>
          ) : (
            <div className="py-2">{fileTree.map((node) => renderTreeNode(node))}</div>
          )}
        </div>
      </div>
    </div>
  );
}
