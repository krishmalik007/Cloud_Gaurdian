import React from 'react';
import { Table } from '../ui/Table';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import IncidentSeverityBadge from '../incidents/IncidentSeverityBadge';
import { HiOutlineEye } from 'react-icons/hi';

export default function EventsTable({
  events = [],
  loading = false,
  onViewDetails,
}) {
  const getProviderVariant = (provider) => {
    const p = String(provider).toUpperCase();
    if (p === 'AWS') return 'warning';
    if (p === 'AZURE') return 'info';
    if (p === 'GCP') return 'purple';
    return 'muted';
  };

  const getStatusVariant = (status) => {
    const s = String(status).toUpperCase();
    if (s === 'INFORMATIONAL') return 'muted';
    if (s === 'OPERATIONAL_HEALTH') return 'info';
    if (s === 'OPEN' || s === 'SUSPICIOUS') return 'warning';
    if (s === 'RESOLVED') return 'success';
    return 'muted';
  };

  const columns = [
    {
      header: 'Event Name',
      accessor: 'event_name',
      render: (item) => (
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-xs text-text-primary">
              {item.event_name || 'CloudEvent'}
            </span>
            {item.is_incident && (
              <span className="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded bg-red/10 text-red border border-red/20">
                Alert
              </span>
            )}
          </div>
          <span className="font-mono text-[10px] text-text-muted truncate max-w-[200px]">
            {item.event_id}
          </span>
        </div>
      ),
    },
    {
      header: 'Provider',
      accessor: 'provider',
      render: (item) => (
        <Badge variant={getProviderVariant(item.provider)} size="sm">
          {String(item.provider || 'AWS').toUpperCase()}
        </Badge>
      ),
    },
    {
      header: 'Principal / User',
      accessor: 'username',
      render: (item) => (
        <span className="font-mono text-xs text-text-secondary truncate max-w-[160px] block" title={item.username}>
          {item.username || 'System / Service'}
        </span>
      ),
    },
    {
      header: 'Region',
      accessor: 'region',
      render: (item) => (
        <span className="font-mono text-xs text-text-muted">
          {item.region || item.event_summary?.region || 'Unknown'}
        </span>
      ),
    },
    {
      header: 'Source IP',
      accessor: 'source_ip',
      render: (item) => (
        <span className="font-mono text-xs text-text-muted truncate max-w-[120px] block" title={item.source_ip || item.event_summary?.source_ip}>
          {item.source_ip || item.event_summary?.source_ip || '-'}
        </span>
      ),
    },
    {
      header: 'Severity',
      accessor: 'risk_level',
      render: (item) => (
        <IncidentSeverityBadge severity={item.risk_level || 'LOW'} size="sm" />
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (item) => (
        <Badge variant={getStatusVariant(item.status)} size="sm">
          {item.status || 'INFORMATIONAL'}
        </Badge>
      ),
    },
    {
      header: 'Timestamp',
      accessor: 'timestamp',
      render: (item) => {
        const timeVal = item.timestamp || item.event_summary?.timestamp || item.ingested_at;
        return (
          <span className="text-xs text-text-muted whitespace-nowrap">
            {timeVal
              ? new Date(timeVal).toLocaleString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                })
              : '-'}
          </span>
        );
      },
    },
    {
      header: 'Actions',
      accessor: 'event_id',
      render: (item) => (
        <Button
          variant="outline"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onViewDetails(item);
          }}
          className="py-1 px-2.5 text-xs flex items-center gap-1.5"
        >
          <HiOutlineEye className="w-3.5 h-3.5" />
          Inspect
        </Button>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={events}
      isLoading={loading}
      emptyMessage="No Cloud Events Found"
      emptySubMessage="Ingested telemetry events will appear here in real time."
      onRowClick={(item) => onViewDetails(item)}
    />
  );
}
