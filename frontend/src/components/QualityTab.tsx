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

  // Add safe defaults for complexity_distribution
  const complexityDist = dashboard.complexity_distribution || {};
  const maintainabilityDist = dashboard.maintainability_distribution || {};

  // Define average metrics safely
  const avgComplexity = dashboard.average_complexity ?? 0;
  const avgMaintainability = dashboard.average_maintainability ?? 0;

  // Prepare chart data with safe accessors
  const complexityData = [
    { 
      name: 'Simple (1-10)', 
      value: complexityDist['simple (1-10)'] || 0, 
      color: '#10b981',
      label: 'Simple'
    },
    { 
      name: 'Moderate (11-20)', 
      value: complexityDist['moderate (11-20)'] || 0, 
      color: '#f59e0b',
      label: 'Moderate'
    },
    { 
      name: 'Complex (21-50)', 
      value: complexityDist['complex (21-50)'] || 0, 
      color: '#f97316',
      label: 'Complex'
    },
    { 
      name: 'Very Complex (50+)', 
      value: complexityDist['very_complex (50+)'] || 0, 
      color: '#ef4444',
      label: 'Very Complex'
    },
  ];

  const maintainabilityData = [
    { name: 'Excellent (85-100)', value: maintainabilityDist['excellent (85-100)'] || 0, color: '#10b981' },
    { name: 'Good (65-84)', value: maintainabilityDist['good (65-84)'] || 0, color: '#f59e0b' },
    { name: 'Fair (50-64)', value: maintainabilityDist['fair (50-64)'] || 0, color: '#f97316' },
    { name: 'Poor (<50)', value: maintainabilityDist['poor (<50)'] || 0, color: '#ef4444' },
  ];

  // Calculate total for percentages
  const totalComplexity = complexityData.reduce((sum, item) => sum + item.value, 0);

  // If no data at all, show message
  if (totalComplexity === 0 && dashboard.total_symbols === 0) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-16 h-16 text-slate-400 mx-auto mb-4" />
        <p className="text-slate-600 dark:text-slate-400 mb-2">No code analysis data available</p>
        <p className="text-sm text-slate-500">This repository may still be processing or failed to import.</p>
      </div>
    );
  }

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
            {avgComplexity.toFixed(1)}
          </p>
        </div>
        <div className="bg-slate-50 dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Avg Maintainability</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {avgMaintainability.toFixed(1)}
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
          <div className="flex flex-col items-center">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={complexityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ percent }) => percent > 0 ? `${(percent * 100).toFixed(0)}%` : ''}
                  outerRadius={90}
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
            
            {/* Custom Legend with better spacing */}
            <div className="grid grid-cols-2 gap-x-6 gap-y-3 mt-4 w-full max-w-md">
              {complexityData.map((item, index) => {
                const percentage = totalComplexity > 0 ? ((item.value / totalComplexity) * 100).toFixed(0) : 0;
                return (
                  <div key={index} className="flex items-center gap-3">
                    <div 
                      className="w-4 h-4 rounded-sm flex-shrink-0" 
                      style={{ backgroundColor: item.color }}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 dark:text-white leading-tight">
                        {item.label}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {item.name.match(/\\(([^)]+)\\)/)?.[1]}: {percentage}%
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Maintainability Distribution */}
        <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6">
            Maintainability Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={maintainabilityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis 
                dataKey="name" 
                angle={-45} 
                textAnchor="end" 
                height={100}
                tick={{ fontSize: 12, fill: '#94a3b8' }}
              />
              <YAxis tick={{ fontSize: 12, fill: '#94a3b8' }} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Bar dataKey="value" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
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
                  <div className="flex-1 min-w-0 mr-4">
                    <p className="font-mono font-semibold text-slate-900 dark:text-white truncate">
                      {func.name}
                    </p>
                    <p className="text-sm text-slate-600 dark:text-slate-400 truncate">{func.file_path}</p>
                  </div>
                  <div className="flex gap-4 flex-shrink-0">
                    <div className="text-right">
                      <p className="text-xs text-slate-500 dark:text-slate-400">Complexity</p>
                      <p className="text-lg font-bold text-orange-600">{func.complexity}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-500 dark:text-slate-400">Maintainability</p>
                      <p className="text-lg font-bold text-blue-600">
                        {func.maintainability.toFixed(0)}
                      </p>
                    </div>
                  </div>
                </div>
                {func.signature && (
                  <pre className="text-xs text-slate-600 dark:text-slate-400 overflow-x-auto bg-slate-100 dark:bg-slate-800 p-2 rounded mt-2">
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
