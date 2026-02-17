import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Shield,
  AlertTriangle,
  AlertOctagon,
  Info,
  X,
  PlayCircle,
  Loader2,
  FileCode,
  ChevronDown,
  ChevronUp,
  Filter,
} from 'lucide-react';
import { securityApi, Vulnerability, SecurityStats } from '../services/securityApi';

export function SecurityTab() {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [stats, setStats] = useState<SecurityStats | null>(null);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [expandedVuln, setExpandedVuln] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadSecurityData();
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      loadVulnerabilities();
    }
  }, [id, selectedSeverity, selectedType]);

  const loadSecurityData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const statsData = await securityApi.getSecurityStats(id);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load security stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadVulnerabilities = async () => {
    if (!id) return;
    try {
      const data = await securityApi.getVulnerabilities(
        id,
        selectedSeverity || undefined,
        selectedType || undefined
      );
      setVulnerabilities(data.vulnerabilities);
    } catch (error) {
      console.error('Failed to load vulnerabilities:', error);
    }
  };

  const handleScan = async () => {
    if (!id) return;
    try {
      setScanning(true);
      await securityApi.scanRepository(id);
      // Wait 2 seconds for scan to process
      setTimeout(async () => {
        await loadSecurityData();
        await loadVulnerabilities();
        setScanning(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to trigger scan:', error);
      setScanning(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300';
      case 'high':
        return 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800 text-orange-700 dark:text-orange-300';
      case 'medium':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-300';
      case 'low':
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300';
      default:
        return 'bg-slate-50 dark:bg-slate-900/20 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertOctagon className="w-5 h-5 text-red-600 dark:text-red-400" />;
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400" />;
      case 'medium':
        return <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />;
      case 'low':
        return <Info className="w-5 h-5 text-blue-600 dark:text-blue-400" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
        <p className="text-slate-600 dark:text-slate-400">Loading security analysis...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Shield className="w-6 h-6 text-blue-600" />
          Security Analysis
        </h3>
        <button
          onClick={handleScan}
          disabled={scanning}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white rounded-lg font-semibold transition-colors"
        >
          {scanning ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Scanning...
            </>
          ) : (
            <>
              <PlayCircle className="w-5 h-5" />
              Run Security Scan
            </>
          )}
        </button>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-red-50 dark:bg-red-900/20 p-6 rounded-xl border border-red-200 dark:border-red-800">
            <AlertOctagon className="w-8 h-8 text-red-600 dark:text-red-400 mb-4" />
            <p className="text-sm text-red-700 dark:text-red-300 mb-2">Critical</p>
            <p className="text-3xl font-bold text-red-600 dark:text-red-400">
              {stats.by_severity.critical}
            </p>
          </div>
          <div className="bg-orange-50 dark:bg-orange-900/20 p-6 rounded-xl border border-orange-200 dark:border-orange-800">
            <AlertTriangle className="w-8 h-8 text-orange-600 dark:text-orange-400 mb-4" />
            <p className="text-sm text-orange-700 dark:text-orange-300 mb-2">High</p>
            <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">
              {stats.by_severity.high}
            </p>
          </div>
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-6 rounded-xl border border-yellow-200 dark:border-yellow-800">
            <AlertTriangle className="w-8 h-8 text-yellow-600 dark:text-yellow-400 mb-4" />
            <p className="text-sm text-yellow-700 dark:text-yellow-300 mb-2">Medium</p>
            <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
              {stats.by_severity.medium}
            </p>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-xl border border-blue-200 dark:border-blue-800">
            <Info className="w-8 h-8 text-blue-600 dark:text-blue-400 mb-4" />
            <p className="text-sm text-blue-700 dark:text-blue-300 mb-2">Low</p>
            <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {stats.by_severity.low}
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
        <Filter className="w-5 h-5 text-slate-600 dark:text-slate-400" />
        <select
          value={selectedSeverity}
          onChange={(e) => setSelectedSeverity(e.target.value)}
          className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
        >
          <option value="">All Types</option>
          <option value="SQL Injection">SQL Injection</option>
          <option value="Hardcoded Secret">Hardcoded Secret</option>
          <option value="Command Injection">Command Injection</option>
          <option value="Path Traversal">Path Traversal</option>
          <option value="XSS">XSS</option>
        </select>
        {(selectedSeverity || selectedType) && (
          <button
            onClick={() => {
              setSelectedSeverity('');
              setSelectedType('');
            }}
            className="flex items-center gap-2 px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
          >
            <X className="w-4 h-4" />
            Clear Filters
          </button>
        )}
      </div>

      {/* Vulnerabilities List */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-slate-900 dark:text-white">
          Vulnerabilities ({vulnerabilities.length})
        </h4>

        {vulnerabilities.length === 0 ? (
          <div className="text-center py-12 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
            <Shield className="w-16 h-16 text-green-600 dark:text-green-400 mx-auto mb-4" />
            <p className="text-lg font-semibold text-green-900 dark:text-green-100 mb-2">
              No vulnerabilities found!
            </p>
            <p className="text-green-700 dark:text-green-300">
              Your code looks secure. Run a scan to check for new issues.
            </p>
          </div>
        ) : (
          vulnerabilities.map((vuln) => (
            <div
              key={vuln.id}
              className={`p-6 rounded-xl border-2 ${getSeverityColor(vuln.severity)} transition-all`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-4 flex-1">
                  <div className="flex-shrink-0 mt-1">{getSeverityIcon(vuln.severity)}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h5 className="font-bold text-lg">{vuln.type}</h5>
                      <span className="px-3 py-1 rounded-full text-xs font-semibold uppercase">
                        {vuln.severity}
                      </span>
                      <span className="px-3 py-1 rounded-full text-xs bg-slate-200 dark:bg-slate-700">
                        {vuln.cwe_id}
                      </span>
                    </div>
                    <p className="text-sm mb-3">{vuln.description}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <FileCode className="w-4 h-4" />
                        <span className="font-mono">{vuln.file_path}</span>
                      </div>
                      <span className="px-2 py-1 bg-slate-200 dark:bg-slate-700 rounded">Line {vuln.line_number}</span>
                      <span className="text-xs opacity-75">{vuln.owasp_category}</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setExpandedVuln(expandedVuln === vuln.id ? null : vuln.id)}
                  className="ml-4 p-2 hover:bg-white/50 dark:hover:bg-slate-800/50 rounded-lg transition-colors"
                >
                  {expandedVuln === vuln.id ? (
                    <ChevronUp className="w-5 h-5" />
                  ) : (
                    <ChevronDown className="w-5 h-5" />
                  )}
                </button>
              </div>

              {expandedVuln === vuln.id && (
                <div className="mt-4 pt-4 border-t border-slate-300 dark:border-slate-600 space-y-4">
                  <div>
                    <h6 className="font-semibold mb-2 flex items-center gap-2">
                      <FileCode className="w-4 h-4" />
                      Code Snippet
                    </h6>
                    <pre className="p-4 bg-slate-900 dark:bg-slate-950 text-slate-100 rounded-lg overflow-x-auto text-sm">
                      <code>{vuln.code_snippet}</code>
                    </pre>
                  </div>
                  <div>
                    <h6 className="font-semibold mb-2 flex items-center gap-2">
                      <Shield className="w-4 h-4" />
                      Recommendation
                    </h6>
                    <p className="text-sm p-4 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                      {vuln.recommendation}
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="px-3 py-1 bg-slate-200 dark:bg-slate-700 rounded-full">
                      Confidence: {vuln.confidence}
                    </span>
                    <span className="opacity-75">
                      Detected: {new Date(vuln.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
