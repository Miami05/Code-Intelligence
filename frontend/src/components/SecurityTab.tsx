import { Shield, AlertTriangle, Info } from 'lucide-react';

export function SecurityTab() {
  return (
    <div className="space-y-6">
      {/* Info Banner */}
      <div className="p-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl flex items-start gap-4">
        <Info className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-1" />
        <div>
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
            Security Analysis Coming Soon
          </h3>
          <p className="text-blue-700 dark:text-blue-300 text-sm">
            Security vulnerability detection and code smell analysis will be available in the next
            sprint. This will include:
          </p>
          <ul className="mt-3 space-y-1 text-sm text-blue-700 dark:text-blue-300">
            <li>• SQL injection detection</li>
            <li>• XSS vulnerability scanning</li>
            <li>• Hardcoded secrets detection</li>
            <li>• Insecure dependencies</li>
            <li>• Code smell identification</li>
          </ul>
        </div>
      </div>

      {/* Placeholder Security Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-green-50 dark:bg-green-900/20 p-6 rounded-xl border border-green-200 dark:border-green-800">
          <Shield className="w-8 h-8 text-green-600 dark:text-green-400 mb-4" />
          <p className="text-sm text-green-700 dark:text-green-300 mb-2">Security Score</p>
          <p className="text-3xl font-bold text-green-600 dark:text-green-400">-</p>
        </div>
        <div className="bg-orange-50 dark:bg-orange-900/20 p-6 rounded-xl border border-orange-200 dark:border-orange-800">
          <AlertTriangle className="w-8 h-8 text-orange-600 dark:text-orange-400 mb-4" />
          <p className="text-sm text-orange-700 dark:text-orange-300 mb-2">Vulnerabilities</p>
          <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">-</p>
        </div>
        <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-xl border border-blue-200 dark:border-blue-800">
          <Info className="w-8 h-8 text-blue-600 dark:text-blue-400 mb-4" />
          <p className="text-sm text-blue-700 dark:text-blue-300 mb-2">Code Smells</p>
          <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">-</p>
        </div>
      </div>
    </div>
  );
}
