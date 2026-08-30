import React, { useState } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { toast } from 'react-toastify';
import { HiOutlineAdjustments, HiOutlineBell, HiOutlineDatabase, HiOutlineRefresh } from 'react-icons/hi';

export default function Settings() {
  // Persist settings locally
  const [refreshInterval, setRefreshInterval] = useState(() => {
    return localStorage.getItem('cg_settings_refresh') || '30';
  });
  
  const [riskThreshold, setRiskThreshold] = useState(() => {
    return localStorage.getItem('cg_settings_threshold') || '75';
  });

  const [notifications, setNotifications] = useState(() => {
    try {
      const stored = localStorage.getItem('cg_settings_notifications');
      return stored ? JSON.parse(stored) : { email: true, slack: false, alerts: true };
    } catch {
      return { email: true, slack: false, alerts: true };
    }
  });

  const handleSave = () => {
    localStorage.setItem('cg_settings_refresh', refreshInterval);
    localStorage.setItem('cg_settings_threshold', riskThreshold);
    localStorage.setItem('cg_settings_notifications', JSON.stringify(notifications));
    toast.success('SOC settings saved successfully.');
  };

  return (
    <div className="flex flex-col gap-6 text-left select-none">
      <PageHeader
        title="SOC Configuration Settings"
        subtitle="Manage alerts correlation settings, API thresholds, and system integration variables."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Thresholds & Refresh Config */}
        <Card title="Operational Settings" className="bg-surface/30">
          <div className="flex flex-col gap-5 pt-2">
            {/* Auto refresh dropdown */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-1.5">
                <HiOutlineRefresh className="w-4.5 h-4.5 text-primary-blue" />
                Live Feed Refresh Interval
              </label>
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(e.target.value)}
                className="bg-background border border-border-color rounded-lg px-3 py-2 text-xs text-text-primary outline-none focus:border-primary-blue w-full"
              >
                <option value="10">Every 10 seconds</option>
                <option value="30">Every 30 seconds</option>
                <option value="60">Every 60 seconds</option>
                <option value="0">Manual Refresh Only</option>
              </select>
            </div>

            {/* Risk Threshold Slider */}
            <div className="flex flex-col gap-2">
              <div className="flex justify-between">
                <label className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-1.5">
                  <HiOutlineAdjustments className="w-4.5 h-4.5 text-primary-blue" />
                  Critical Alert Trigger Threshold
                </label>
                <span className="text-xs font-bold text-primary-blue">{riskThreshold}%</span>
              </div>
              <input
                type="range"
                min="50"
                max="95"
                step="5"
                value={riskThreshold}
                onChange={(e) => setRiskThreshold(e.target.value)}
                className="w-full h-1.5 bg-background rounded-lg appearance-none cursor-pointer accent-primary-blue border border-border-color"
              />
              <span className="text-[10px] text-text-muted">
                Incidents scoring equal or above this threshold generate Critical Severity warnings.
              </span>
            </div>
          </div>
        </Card>

        {/* Integration Notification Toggles */}
        <Card title="Notification Integrations" className="bg-surface/30">
          <div className="flex flex-col gap-4 pt-2">
            <div className="flex items-center justify-between p-3 rounded-lg border border-border-color bg-background/30">
              <div className="flex flex-col gap-0.5">
                <span className="text-xs font-semibold text-text-primary flex items-center gap-1.5">
                  <HiOutlineBell className="w-4 h-4 text-primary-blue" />
                  Email Subscriptions
                </span>
                <span className="text-[10px] text-text-muted">Receive daily alert digests in your inbox.</span>
              </div>
              <input
                type="checkbox"
                checked={notifications.email}
                onChange={(e) => setNotifications({ ...notifications, email: e.target.checked })}
                className="w-4 h-4 accent-primary-blue cursor-pointer"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg border border-border-color bg-background/30">
              <div className="flex flex-col gap-0.5">
                <span className="text-xs font-semibold text-text-primary flex items-center gap-1.5">
                  <HiOutlineDatabase className="w-4 h-4 text-primary-blue" />
                  OpenSearch Index Sync alerts
                </span>
                <span className="text-[10px] text-text-muted">Generate error notifications for sync timeouts.</span>
              </div>
              <input
                type="checkbox"
                checked={notifications.alerts}
                onChange={(e) => setNotifications({ ...notifications, alerts: e.target.checked })}
                className="w-4 h-4 accent-primary-blue cursor-pointer"
              />
            </div>
          </div>
        </Card>
      </div>

      <div className="flex items-center justify-end gap-3 border-t border-border-color/30 pt-5 mt-4">
        <Button variant="primary" size="sm" onClick={handleSave}>
          Save Settings
        </Button>
      </div>
    </div>
  );
}
