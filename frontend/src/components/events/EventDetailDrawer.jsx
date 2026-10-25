import React from 'react';
import { HiOutlineX, HiOutlineInformationCircle, HiOutlineClock, HiOutlineUser, HiOutlineGlobe, HiOutlineShieldCheck } from 'react-icons/hi';
import { Badge } from '../ui/Badge';
import IncidentSeverityBadge from '../incidents/IncidentSeverityBadge';

export default function EventDetailDrawer({ isOpen, onClose, event }) {
  if (!isOpen || !event) return null;

  const eventName = event.event_name || 'CloudEvent';
  const provider = (event.provider || 'AWS').toUpperCase();
  const timestamp = event.timestamp || event.event_summary?.timestamp || event.ingested_at;

  const getProviderVariant = (p) => {
    if (p === 'AWS') return 'warning';
    if (p === 'AZURE') return 'info';
    if (p === 'GCP') return 'purple';
    return 'muted';
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Drawer Panel */}
      <aside className="fixed inset-y-0 right-0 z-50 w-full max-w-2xl bg-sidebar border-l border-border-color shadow-2xl flex flex-col animate-slide-left select-text">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border-color bg-surface/30">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary-blue/10 border border-primary-blue/20 text-primary-blue">
              <HiOutlineInformationCircle className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-bold text-text-primary flex items-center gap-2">
                {eventName}
                {event.is_incident && (
                  <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 rounded-full bg-red/10 text-red border border-red/20">
                    Incident
                  </span>
                )}
              </h2>
              <span className="text-xs text-text-muted font-mono">{event.event_id}</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface transition-colors cursor-pointer"
          >
            <HiOutlineX className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
          {/* Metadata Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-lg bg-surface/40 border border-border-color">
              <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider block">Provider</span>
              <div className="mt-1">
                <Badge variant={getProviderVariant(provider)} size="sm">
                  {provider}
                </Badge>
              </div>
            </div>
            <div className="p-3 rounded-lg bg-surface/40 border border-border-color">
              <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider block">Status</span>
              <span className={`text-xs font-bold mt-1 block ${event.is_incident ? 'text-red' : 'text-green'}`}>
                {event.status || 'INFORMATIONAL'}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-surface/40 border border-border-color">
              <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider block">Severity</span>
              <div className="mt-1">
                <IncidentSeverityBadge severity={event.risk_level || 'LOW'} size="sm" />
              </div>
            </div>
            <div className="p-3 rounded-lg bg-surface/40 border border-border-color">
              <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider block">Risk Score</span>
              <span className="text-xs font-extrabold text-text-primary mt-1 block">
                {event.risk_score || 0} / 100
              </span>
            </div>
          </div>

          {/* Key Details List */}
          <div className="flex flex-col gap-3 p-4 rounded-xl bg-surface/20 border border-border-color">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
              Event Context & Identity
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="flex items-center gap-2 text-text-secondary">
                <HiOutlineUser className="w-4 h-4 text-text-muted flex-shrink-0" />
                <span className="font-semibold text-text-muted">Principal:</span>
                <span className="font-mono text-text-primary truncate">{event.username || 'N/A'}</span>
              </div>
              <div className="flex items-center gap-2 text-text-secondary">
                <HiOutlineGlobe className="w-4 h-4 text-text-muted flex-shrink-0" />
                <span className="font-semibold text-text-muted">Region:</span>
                <span className="font-mono text-text-primary">{event.region || event.event_summary?.region || 'Unknown'}</span>
              </div>
              <div className="flex items-center gap-2 text-text-secondary">
                <HiOutlineShieldCheck className="w-4 h-4 text-text-muted flex-shrink-0" />
                <span className="font-semibold text-text-muted">Source IP:</span>
                <span className="font-mono text-text-primary">{event.source_ip || event.event_summary?.source_ip || 'Internal Service'}</span>
              </div>
              <div className="flex items-center gap-2 text-text-secondary">
                <HiOutlineClock className="w-4 h-4 text-text-muted flex-shrink-0" />
                <span className="font-semibold text-text-muted">Timestamp:</span>
                <span className="text-text-primary">
                  {timestamp ? new Date(timestamp).toLocaleString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Raw Log Payload */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">
                Sanitized Raw Audit Payload
              </h3>
              <span className="text-[10px] text-text-muted">OpenSearch `events` index</span>
            </div>
            <pre className="p-4 rounded-xl bg-background border border-border-color text-[11px] font-mono text-text-secondary overflow-x-auto max-h-96 leading-relaxed">
              {JSON.stringify(event.raw_log || event, null, 2)}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border-color bg-surface/30 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-surface hover:bg-background border border-border-color text-text-secondary hover:text-text-primary transition-colors cursor-pointer"
          >
            Close Inspector
          </button>
        </div>
      </aside>
    </>
  );
}
