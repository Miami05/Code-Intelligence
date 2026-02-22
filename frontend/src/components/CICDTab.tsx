import React, { useState, useEffect, useCallback } from 'react';
import {
  GitBranch,
  ShieldCheck,
  ShieldX,
  Play,
  Settings,
  History,
  ExternalLink,
  Bell,
  Save,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
} from 'lucide-react';
import {
  cicdApi,
  QualityGateConfig,
  QualityGateResult,
  CICDRun,
} from '../services/cicdApi';

interface Props {
  repositoryId: string;
}

const DEFAULT_CONFIG: QualityGateConfig = {
  max_complexity: 10,
  max_code_smells: 20,
  max_critical_smells: 0,
  max_vulnerabilities: 5,
  max_critical_vulnerabilities: 0,
  min_quality_score: 70.0,
  max_duplication_percentage: 10.0,
  block_on_failure: true,
};

export const CICDTab: React.FC<Props> = ({ repositoryId }) => {
  const [activeSection, setActiveSection] = useState<'gate' | 'runs' | 'notify'>('gate');

  // --- Quality Gate state ---
  const [config, setConfig] = useState<QualityGateConfig>(DEFAULT_CONFIG);
  const [configLoading, setConfigLoading] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  // --- Run check state ---
  const [checking, setChecking] = useState(false);
  const [lastResult, setLastResult] = useState<QualityGateResult | null>(null);

  // --- Run history state ---
  const [runs, setRuns] = useState<CICDRun[]>([]);
  const [runsLoading, setRunsLoading] = useState(false);

  // --- Notification state ---
  const [slackUrl, setSlackUrl] = useState('');
  const [emailAddr, setEmailAddr] = useState('');
  const [notifMsg, setNotifMsg] = useState<string | null>(null);
  const [notifSending, setNotifSending] = useState(false);

  const loadConfig = useCallback(async () => {
    setConfigLoading(true);
    try {
      const data = await cicdApi.getQualityGate(repositoryId);
      setConfig(data);
    } catch {
      /* use defaults */
    } finally {
      setConfigLoading(false);
    }
  }, [repositoryId]);

  const loadRuns = useCallback(async () => {
    setRunsLoading(true);
    try {
      const data = await cicdApi.getRuns(repositoryId);
      setRuns(data);
    } catch {
      /* ignore */
    } finally {
      setRunsLoading(false);
    }
  }, [repositoryId]);

  useEffect(() => {
    loadConfig();
    loadRuns();
  }, [loadConfig, loadRuns]);

  const handleSaveConfig = async () => {
    setSavingConfig(true);
    setSaveMsg(null);
    try {
      await cicdApi.updateQualityGate(repositoryId, config);
      setSaveMsg('✅ Settings saved!');
    } catch {
      setSaveMsg('❌ Failed to save settings.');
    } finally {
      setSavingConfig(false);
      setTimeout(() => setSaveMsg(null), 3000);
    }
  };

  const handleRunCheck = async () => {
    setChecking(true);
    setLastResult(null);
    try {
      const result = await cicdApi.runQualityGate(repositoryId);
      setLastResult(result);
      loadRuns();
    } catch {
      alert('Failed to run quality gate check.');
    } finally {
      setChecking(false);
    }
  };

  const handleSlackNotify = async () => {
    if (!slackUrl) return;
    setNotifSending(true);
    setNotifMsg(null);
    try {
      const res = await cicdApi.notifySlack(repositoryId, slackUrl);
      setNotifMsg(res.sent ? '✅ Slack notification sent!' : '❌ Slack webhook failed.');
    } catch {
      setNotifMsg('❌ Failed to send notification.');
    } finally {
      setNotifSending(false);
      setTimeout(() => setNotifMsg(null), 4000);
    }
  };

  const handleEmailNotify = async () => {
    if (!emailAddr) return;
    setNotifSending(true);
    setNotifMsg(null);
    try {
      const res = await cicdApi.notifyEmail(repositoryId, emailAddr);
      setNotifMsg(res.sent ? '✅ Email sent!' : '❌ Email send failed (check SMTP config).');
    } catch {
      setNotifMsg('❌ Failed to send email.');
    } finally {
      setNotifSending(false);
      setTimeout(() => setNotifMsg(null), 4000);
    }
  };

  const numericField = (
    label: string,
    key: keyof QualityGateConfig,
    isFloat = false
  ) => (
    <div>
      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
        {label}
      </label>
      <input
        type="number"
        step={isFloat ? '0.1' : '1'}
        min="0"
        value={config[key] as number}
        onChange={(e) =>
          setConfig((c) => ({
            ...c,
            [key]: isFloat ? parseFloat(e.target.value) : parseInt(e.target.value, 10),
          }))
        }
        className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );

  const sections = [
    { id: 'gate', label: 'Quality Gate', icon: Settings },
    { id: 'runs', label: 'Run History', icon: History },
    { id: 'notify', label: 'Notifications', icon: Bell },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-blue-500" />
            CI/CD Integration
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
            Configure quality gates and monitor pipeline runs
          </p>
        </div>
        <button
          onClick={handleRunCheck}
          disabled={checking}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-sm transition-colors disabled:opacity-50"
        >
          {checking ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          Run Quality Gate
        </button>
      </div>

      {/* Last result banner */}
      {lastResult && (
        <div
          className={`flex items-start gap-3 p-4 rounded-xl border ${
            lastResult.passed
              ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
              : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
          }`}
        >
          {lastResult.passed ? (
            <ShieldCheck className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
          ) : (
            <ShieldX className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
          )}
          <div className="flex-1 min-w-0">
            <p className={`font-semibold ${
              lastResult.passed
                ? 'text-green-800 dark:text-green-300'
                : 'text-red-800 dark:text-red-300'
            }`}>
              {lastResult.summary}
            </p>
            {lastResult.block_merge && (
              <p className="text-xs text-red-600 dark:text-red-400 mt-1 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" /> Merge is blocked
              </p>
            )}
            <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
              {lastResult.checks.map((c) => (
                <div
                  key={c.name}
                  className={`flex items-center justify-between text-xs px-3 py-2 rounded-lg ${
                    c.passed
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                      : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
                  }`}
                >
                  <span className="flex items-center gap-1.5">
                    {c.passed ? (
                      <CheckCircle className="w-3 h-3" />
                    ) : (
                      <XCircle className="w-3 h-3" />
                    )}
                    {c.name}
                  </span>
                  <span className="font-mono font-bold">{c.message}</span>
                </div>
              ))}
            </div>
            {lastResult.run_id && (
              <a
                href={cicdApi.getReportUrl(lastResult.run_id)}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 mt-3 hover:underline"
              >
                <ExternalLink className="w-3 h-3" /> View full report
              </a>
            )}
          </div>
        </div>
      )}

      {/* Section tabs */}
      <div className="flex gap-2 border-b border-slate-200 dark:border-slate-700">
        {sections.map((s) => {
          const Icon = s.icon;
          return (
            <button
              key={s.id}
              onClick={() => setActiveSection(s.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
                activeSection === s.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              {s.label}
            </button>
          );
        })}
      </div>

      {/* ── Quality Gate Settings ─────────────────────────────── */}
      {activeSection === 'gate' && (
        <div className="space-y-6">
          {configLoading ? (
            <div className="flex justify-center py-10">
              <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {numericField('Max Code Smells', 'max_code_smells')}
                {numericField('Max Critical Smells', 'max_critical_smells')}
                {numericField('Max Vulnerabilities', 'max_vulnerabilities')}
                {numericField('Max Critical Vulnerabilities', 'max_critical_vulnerabilities')}
                {numericField('Max Complexity', 'max_complexity')}
                {numericField('Min Quality Score', 'min_quality_score', true)}
                {numericField('Max Duplication %', 'max_duplication_percentage', true)}
              </div>

              <div className="flex items-center gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
                <button
                  role="switch"
                  aria-checked={config.block_on_failure}
                  onClick={() =>
                    setConfig((c) => ({ ...c, block_on_failure: !c.block_on_failure }))
                  }
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    config.block_on_failure ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      config.block_on_failure ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    Block merge on failure
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Prevent merging PRs that fail the quality gate
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleSaveConfig}
                  disabled={savingConfig}
                  className="flex items-center gap-2 px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-sm transition-colors disabled:opacity-50"
                >
                  {savingConfig ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4" />
                  )}
                  Save Settings
                </button>
                {saveMsg && (
                  <span className="text-sm text-slate-600 dark:text-slate-300">{saveMsg}</span>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* ── Run History ───────────────────────────────────────── */}
      {activeSection === 'runs' && (
        <div>
          <div className="flex justify-end mb-4">
            <button
              onClick={loadRuns}
              disabled={runsLoading}
              className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${runsLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {runsLoading ? (
            <div className="flex justify-center py-10">
              <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
            </div>
          ) : runs.length === 0 ? (
            <div className="text-center py-12">
              <div className="inline-flex p-4 bg-slate-50 dark:bg-slate-800/50 rounded-full mb-3">
                <History className="w-8 h-8 text-slate-400" />
              </div>
              <p className="text-slate-500 dark:text-slate-400">
                No runs yet. Trigger one above or push a PR.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 dark:bg-slate-800/70">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">Status</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">Branch / PR</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">Triggered by</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">Date</th>
                    <th className="px-4 py-3 text-left font-semibold text-slate-700 dark:text-slate-300">Report</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                  {runs.map((run) => (
                    <tr
                      key={run.id}
                      className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                    >
                      <td className="px-4 py-3">
                        <StatusBadge status={run.status} passed={run.quality_gate_passed} />
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-col">
                          {run.branch && (
                            <span className="font-mono text-xs text-slate-700 dark:text-slate-300 flex items-center gap-1">
                              <GitBranch className="w-3 h-3" />
                              {run.branch}
                            </span>
                          )}
                          {run.pr_number && (
                            <span className="text-xs text-slate-500 dark:text-slate-400">
                              PR #{run.pr_number}{run.pr_title ? ` — ${run.pr_title}` : ''}
                            </span>
                          )}
                          {!run.branch && !run.pr_number && (
                            <span className="text-xs text-slate-400">—</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 rounded text-xs font-medium bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 capitalize">
                          {run.triggered_by}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(run.created_at).toLocaleString()}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <a
                          href={cicdApi.getReportUrl(run.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          <ExternalLink className="w-3 h-3" />
                          View
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Notifications ─────────────────────────────────────── */}
      {activeSection === 'notify' && (
        <div className="space-y-6">
          {/* Slack */}
          <div className="p-5 bg-white dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-1 flex items-center gap-2">
              <Bell className="w-4 h-4 text-purple-500" />
              Slack Webhook
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
              Send the latest quality gate result to a Slack channel.
            </p>
            <div className="flex gap-2">
              <input
                type="url"
                placeholder="https://hooks.slack.com/services/..."
                value={slackUrl}
                onChange={(e) => setSlackUrl(e.target.value)}
                className="flex-1 px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <button
                onClick={handleSlackNotify}
                disabled={notifSending || !slackUrl}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold text-sm transition-colors disabled:opacity-50"
              >
                {notifSending ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Bell className="w-4 h-4" />}
                Send
              </button>
            </div>
          </div>

          {/* Email */}
          <div className="p-5 bg-white dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-1 flex items-center gap-2">
              <Bell className="w-4 h-4 text-green-500" />
              Email Report
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
              Send a full HTML report to an email address (requires SMTP config).
            </p>
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="you@example.com"
                value={emailAddr}
                onChange={(e) => setEmailAddr(e.target.value)}
                className="flex-1 px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button
                onClick={handleEmailNotify}
                disabled={notifSending || !emailAddr}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold text-sm transition-colors disabled:opacity-50"
              >
                {notifSending ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Bell className="w-4 h-4" />}
                Send
              </button>
            </div>
          </div>

          {notifMsg && (
            <p className="text-sm text-slate-600 dark:text-slate-300">{notifMsg}</p>
          )}
        </div>
      )}
    </div>
  );
};

const StatusBadge: React.FC<{ status: string; passed: boolean | null }> = ({
  status,
  passed,
}) => {
  if (status === 'passed' || passed === true) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400">
        <CheckCircle className="w-3 h-3" /> Passed
      </span>
    );
  }
  if (status === 'failed' || passed === false) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">
        <XCircle className="w-3 h-3" /> Failed
      </span>
    );
  }
  if (status === 'running') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400">
        <RefreshCw className="w-3 h-3 animate-spin" /> Running
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
      <Clock className="w-3 h-3" /> {status}
    </span>
  );
};
