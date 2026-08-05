import React from 'react';
import { useIncidentDetails } from '../../hooks/useIncidents';
import { Drawer } from '../ui/Drawer';
import { Skeleton } from '../ui/Skeleton';
import { Badge } from '../ui/Badge';
import IncidentSeverityBadge from './IncidentSeverityBadge';
import IncidentStatusBadge from './IncidentStatusBadge';
import IncidentTimeline from './IncidentTimeline';
import { HiOutlineTerminal, HiOutlineDatabase, HiOutlineUser, HiOutlineInformationCircle } from 'react-icons/hi';

export default function IncidentDrawer({ isOpen, onClose, incidentId }) {
  const { data: incident, isLoading, isError } = useIncidentDetails(incidentId);

  const getProviderVariant = (provider) => {
    const p = String(provider).toUpperCase();
    if (p === 'AWS') return 'warning';
    if (p === 'AZURE') return 'info';
    if (p === 'GCP') return 'purple';
    return 'muted';
  };

  const getRiskScoreColor = (score) => {
    if (score >= 80) return 'bg-red';
    if (score >= 50) return 'bg-orange';
    return 'bg-green';
  };

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={isLoading ? 'Loading Telemetry...' : `Incident: ${incident?.incident_id || ''}`}
      size="lg"
    >
      {isLoading ? (
        <div className="flex flex-col gap-6 w-full">
          <Skeleton className="h-10 w-2/3" />
          <div className="grid grid-cols-2 gap-4">
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
          </div>
          <Skeleton className="h-40" />
          <Skeleton className="h-32" />
        </div>
      ) : isError || !incident ? (
        <div className="text-center py-12 text-text-muted">
          Failed to fetch incident details. Please check connection.
        </div>
      ) : (
        <div className="flex flex-col gap-6 text-left pb-10 select-none">
          {/* Risk Score Progress Row */}
          <div className="p-4 bg-background/40 border border-border-color rounded-xl flex flex-col gap-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-text-secondary">Incident Risk Priority Score</span>
              <span className="font-bold text-text-primary text-sm">{incident.risk_score}/100</span>
            </div>
            
            {/* Custom progress bar */}
            <div className="w-full bg-surface border border-border-color rounded-full h-2">
              <div
                className={`h-full rounded-full transition-all duration-500 ${getRiskScoreColor(
                  incident.risk_score
                )}`}
                style={{ width: `${incident.risk_score}%` }}
              />
            </div>
          </div>

          {/* Incident Properties Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Left side panel props */}
            <div className="flex flex-col gap-3.5 p-4 border border-border-color rounded-xl bg-surface/20">
              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted font-medium">Provider Network</span>
                <Badge variant={getProviderVariant(incident.provider)} size="sm">
                  {String(incident.provider).toUpperCase()}
                </Badge>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted font-medium">Risk Level</span>
                <IncidentSeverityBadge severity={incident.risk_level} size="sm" />
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted font-medium">Triage Status</span>
                <IncidentStatusBadge status={incident.status} size="sm" />
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted font-medium">Username Identity</span>
                <span className="font-semibold text-text-primary flex items-center gap-1.5">
                  <HiOutlineUser className="w-4 h-4 text-text-muted" />
                  {incident.username || '-'}
                </span>
              </div>
            </div>

            {/* Right side panel props (Unmapped backend fields) */}
            <div className="flex flex-col gap-3.5 p-4 border border-border-color rounded-xl bg-surface/20 relative">
              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted font-medium">Incident Owner</span>
                <span className="text-text-muted font-semibold italic text-[11px]">
                  Unassigned (Not stored in DB)
                </span>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted font-medium">Updated Time</span>
                <span className="text-text-muted font-semibold italic text-[11px]">
                  None (Not stored in DB)
                </span>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted font-medium">Event Priority</span>
                <span className="font-semibold text-text-primary text-[11px] capitalize">
                  {incident.priority || '-'}
                </span>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-text-muted font-medium">Ingested Time</span>
                <span className="font-semibold text-text-secondary text-[10px]">
                  {new Date(incident.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          </div>

          {/* Trigger Alert List */}
          {incident.alerts && incident.alerts.length > 0 && (
            <div className="flex flex-col gap-3">
              <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
                <HiOutlineDatabase className="w-4.5 h-4.5 text-primary-blue" />
                Correlated Security Alerts ({incident.alerts.length})
              </h4>
              <div className="flex flex-col gap-2">
                {incident.alerts.map((alert, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-surface border border-border-color rounded-lg text-xs flex flex-col gap-1 text-left"
                  >
                    <div className="flex items-center justify-between font-semibold">
                      <span className="text-text-primary">{alert.rule_name || 'Correlation Violation'}</span>
                      {alert.severity && (
                        <Badge variant="danger" size="sm">
                          {alert.severity}
                        </Badge>
                      )}
                    </div>
                    {alert.description && (
                      <p className="text-[11px] text-text-secondary mt-0.5">{alert.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chronological Incident Lifecycle */}
          <div className="flex flex-col gap-4 mt-2">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
              <HiOutlineInformationCircle className="w-4.5 h-4.5 text-primary-blue" />
              Operational Triage Timeline
            </h4>
            <div className="pl-2 pt-2">
              <IncidentTimeline createdTime={incident.created_at} />
            </div>
          </div>

          {/* Raw Log Telemetry Viewer */}
          {incident.raw_log && (
            <div className="flex flex-col gap-3 mt-2">
              <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
                <HiOutlineTerminal className="w-4.5 h-4.5 text-primary-blue" />
                Raw Telemetry Stream
              </h4>
              <div className="bg-background/80 border border-border-color rounded-xl p-4 font-mono text-[10px] text-green overflow-x-auto select-all max-h-60 max-w-full">
                <pre>{JSON.stringify(incident.raw_log, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      )}
    </Drawer>
  );
}
