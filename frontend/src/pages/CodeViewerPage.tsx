import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { FileCode } from 'lucide-react';

export default function CodeViewerPage() {
  const { id } = useParams<{ id: string }>();
  const filePath = window.location.pathname.split('/files/')[1];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 p-8">
          <div className="flex items-center gap-4 mb-8">
            <FileCode className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                {filePath || 'Code Viewer'}
              </h1>
              <p className="text-slate-600 dark:text-slate-400">Repository ID: {id}</p>
            </div>
          </div>
          <div className="text-center py-12">
            <p className="text-lg text-slate-600 dark:text-slate-400">
              Code viewer with syntax highlighting will be implemented here
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
