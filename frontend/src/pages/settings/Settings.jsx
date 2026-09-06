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

  const [preferences, setPreferences] = useState(() => {
    try {
      const stored = localStorage.getItem('cg_settings_preferences');
      return stored ? JSON.parse(stored) : { autoRefresh: true, showLowRisk: false, detailLevel: 'standard', defaultView: 'open' };
    } catch {
      return { autoRefresh: true, showLowRisk: false, detailLevel: 'standard', defaultView: 'open' };
    }
  });

  const handleSave = () => {
    try {
      localStorage.setItem('cg_settings_refresh', refreshInterval);
      localStorage.setItem('cg_settings_threshold', riskThreshold);
      localStorage.setItem('cg_settings_preferences', JSON.stringify(preferences));
      localStorage.removeItem('cg_settings_notifications');
      toast.success('SOC settings saved successfully.');
    } catch (e) {
      toast.error('Failed to save settings.');
    }
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
                <option value="5">Every 5 seconds</option>
                <option value="10">Every 10 seconds</option>
                <option value="30">Every 30 seconds</option>
                <option value="60">Every 60 seconds</option>
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

        {/* SOC & Security Preferences */}
        <Card title="SOC & Security Preferences" className="bg-surface/30">
          <div className="flex flex-col gap-5 pt-2">
            
            <div className="flex items-center justify-between p-3 rounded-lg border border-border-color bg-background/30">
              <div className="flex flex-col gap-0.5">
                <span className="text-xs font-semibold text-text-primary">
                  Incident Auto-Refresh
                </span>
                <span className="text-[10px] text-text-muted">Automatically refresh incident data when new activity is detected.</span>
              </div>
              <input
                type="checkbox"
                checked={preferences.autoRefresh}
                onChange={(e) => setPreferences({ ...preferences, autoRefresh: e.target.checked })}
                className="w-4 h-4 accent-primary-blue cursor-pointer"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg border border-border-color bg-background/30">
              <div className="flex flex-col gap-0.5">
                <span className="text-xs font-semibold text-text-primary">
                  Show Low-Risk Incidents
                </span>
                <span className="text-[10px] text-text-muted">Display low-risk security events in incident lists and dashboards.</span>
              </div>
              <input
                type="checkbox"
                checked={preferences.showLowRisk}
                onChange={(e) => setPreferences({ ...preferences, showLowRisk: e.target.checked })}
                className="w-4 h-4 accent-primary-blue cursor-pointer"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-text-primary">
                Incident Detail Level
              </label>
              <select
                value={preferences.detailLevel}
                onChange={(e) => setPreferences({ ...preferences, detailLevel: e.target.value })}
                className="bg-background border border-border-color rounded-lg px-3 py-2 text-xs text-text-primary outline-none focus:border-primary-blue w-full"
              >
                <option value="standard">Standard</option>
                <option value="detailed">Detailed</option>
              </select>
              <span className="text-[10px] text-text-muted mt-1">Controls how much event and correlation information is displayed in investigations.</span>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-text-primary">
                Default Incident View
              </label>
              <select
                value={preferences.defaultView}
                onChange={(e) => setPreferences({ ...preferences, defaultView: e.target.value })}
                className="bg-background border border-border-color rounded-lg px-3 py-2 text-xs text-text-primary outline-none focus:border-primary-blue w-full"
              >
                <option value="all">All Incidents</option>
                <option value="open">Open Incidents</option>
                <option value="critical">High & Critical</option>
              </select>
              <span className="text-[10px] text-text-muted mt-1">Choose which incidents are shown by default when opening the Incidents page.</span>
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
