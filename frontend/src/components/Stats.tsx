import React from "react";
import { BarChart3, Clock, Target } from "lucide-react";

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
    <div className="grid grid-cols-3 gap-4 mb-8">
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <BarChart3 className="w-8 h-8 text-primary" />
          <div>
            <p className="text-gray-400 text-sm">Results</p>
            <p className="text-2xl font-bold text-white">{totalResults}</p>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <Clock className="w-8 h-8 text-green-400" />
          <div>
            <p className="text-gray-400 text-sm">Search Time</p>
            <p className="text-2xl font-bold text-white">
              {searchTime ? `${searchTime}ms` : "-"}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <Target className="w-8 h-8 text-purple-400" />
          <div>
            <p className="text-gray-400 text-sm">Threshold</p>
            <p className="text-2xl font-bold text-white">
              {threshold.toFixed(1)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
