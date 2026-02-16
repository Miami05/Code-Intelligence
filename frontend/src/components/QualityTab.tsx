import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { repositoryApi } from '../services/repositoryApi';
import { QualityDashboard, ComplexFunction } from '../types/repository';

export function QualityTab() {
  const { id } = useParams<{ id: string }>();
  const [dashboard, setDashboard] = useState<QualityDashboard | null>(null);
  const [complexFunctions, setComplexFunctions] = useState<ComplexFunction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadQualityData();
    }
  }, [id]);

  const loadQualityData = async () => {
    if (!id) return;
    try {
      const [dashboardData, complexData] = await Promise.all([
        repositoryApi.getQualityDashboard(id),
        repositoryApi.getComplexFunctions(id, 20, 10),
      ]);
      setDashboard(dashboardData);
      setComplexFunctions(complexData.functions || []);
    } catch (error) {
      console.error('Failed to load quality data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-slate-600 dark:text-slate-400">Loading quality metrics...</p>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-16 h-16 text-slate-400 mx-auto mb-4" />
        <p className="text-slate-600 dark:text-slate-400">No quality data available</p>
      </div>
    );
  }

  // Prepare chart data
  const complexityData = [
    { name: 'Simple (1-10)', value: dashboard.complexity_distribution['simple (1-10)'], color: '#10b981' },
    { name: 'Moderate (11-20)', value: dashboard.complexity_distribution['moderate (11-20)'], color: '#f59e0b' },
    { name: 'Complex (21-50)', value: dashboard.complexity_distribution['complex (21-50)'], color: '#f97316' },
    { name: 'Very Complex (50+)', value: dashboard.complexity_distribution['very_complex (50+)'], color: '#ef4444' },
  ];

  const maintainabilityData = [
    { name: 'Excellent (85-100)', value: dashboard.maintainability_distribution['excellent (85-100)'], color: '#10b981' },
    { name: 'Good (65-84)', value: dashboard.maintainability_distribution['good (65-84)'], color: '#f59e0b' },
    { name: 'Fair (50-64)', value: dashboard.maintainability_distribution['fair (50-64)'], color: '#f97316' },
    { name: 'Poor (<50)', value: dashboard.maintainability_distribution['poor (<50)'], color: '#ef4444' },
  ];

  return (
    <div className="space-y-8">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-50 dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Total Symbols</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {dashboard.total_symbols}
          </p>
        </div>
        <div className="bg-slate-50 dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Avg Complexity</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {dashboard.average_complexity.toFixed(1)}
          </p>
        </div>
        <div className="bg-slate-50 dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Avg Maintainability</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {dashboard.average_maintainability.toFixed(1)}
          </p>
        </div>
        <div className="bg-slate-50 dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Issues</p>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400">
            {dashboard.high_complexity_count + dashboard.low_maintainability_count}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Complexity Distribution */}
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6">
            Complexity Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={complexityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {complexityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Maintainability Distribution */}
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6">
            Maintainability Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={maintainabilityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Complex Functions */}
      {complexFunctions.length > 0 && (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            Most Complex Functions
          </h3>
          <div className="space-y-3">
            {complexFunctions.map((func) => (
              <div
                key={func.symbol_id}
                className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-mono font-semibold text-slate-900 dark:text-white">
                      {func.name}
                    </p>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{func.file_path}</p>
                  </div>
                  <div className="flex gap-4">
                    <div className="text-right">
                      <p className="text-xs text-slate-500">Complexity</p>
                      <p className="text-lg font-bold text-orange-600">{func.complexity}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-500">Maintainability</p>
                      <p className="text-lg font-bold text-blue-600">
                        {func.maintainability.toFixed(0)}
                      </p>
                    </div>
                  </div>
                </div>
                {func.signature && (
                  <pre className="text-xs text-slate-600 dark:text-slate-400 overflow-x-auto">
                    {func.signature}
                  </pre>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
