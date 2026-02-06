import React from "react";
import { Clock, Target, TrendingUp } from "lucide-react";

interface StatsProps {
  totalResults: number;
  searchTime?: number;
  threshold: number;
}

export const Stats: React.FC<StatsProps> = ({
  totalResults,
  searchTime,
  threshold,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-2 border-blue-200 dark:border-blue-800 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-500 rounded-lg">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Results Found</span>
        </div>
        <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">{totalResults}</p>
      </div>

      {searchTime && (
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-2 border-purple-200 dark:border-purple-800 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500 rounded-lg">
              <Clock className="w-5 h-5 text-white" />
            </div>
            <span className="text-sm font-medium text-purple-700 dark:text-purple-300">Search Time</span>
          </div>
          <p className="text-3xl font-bold text-purple-900 dark:text-purple-100">{searchTime}ms</p>
        </div>
      )}

      <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-2 border-green-200 dark:border-green-800 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-green-500 rounded-lg">
            <Target className="w-5 h-5 text-white" />
          </div>
          <span className="text-sm font-medium text-green-700 dark:text-green-300">Threshold</span>
        </div>
        <p className="text-3xl font-bold text-green-900 dark:text-green-100">{(threshold * 100).toFixed(0)}%</p>
      </div>
    </div>
  );
};
