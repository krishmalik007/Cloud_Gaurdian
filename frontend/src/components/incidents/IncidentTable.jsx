import React from 'react';
import { Table } from '../ui/Table';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import IncidentSeverityBadge from './IncidentSeverityBadge';
import IncidentStatusBadge from './IncidentStatusBadge';
import { useAuth } from '../../context/AuthContext';
import { ROLES } from '../../constants/roles';

export default function IncidentTable({
  incidents = [],
  loading = false,
  onViewDetails,
  onDelete,
}) {
  const { user } = useAuth();

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

  const columns = [
    {
      header: 'Incident ID',
      accessor: 'incident_id',
      render: (item) => (
        <span className="font-mono text-xs font-semibold text-text-primary select-all">
          {item.incident_id}
        </span>
      ),
    },
    {
      header: 'Provider',
      accessor: 'provider',
      render: (item) => (
        <Badge variant={getProviderVariant(item.provider)} size="sm">
          {String(item.provider).toUpperCase()}
        </Badge>
      ),
    },
    {
      header: 'Severity',
      accessor: 'risk_level',
      render: (item) => (
        <IncidentSeverityBadge severity={item.risk_level} size="sm" />
      ),
    },
    {
      header: 'Risk Score',
      accessor: 'risk_score',
      render: (item) => (
        <div className="flex items-center gap-2 w-20">
          <div className="w-full bg-background border border-border-color rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full ${getRiskScoreColor(item.risk_score)}`}
              style={{ width: `${item.risk_score}%` }}
            />
          </div>
          <span className="text-[10px] font-semibold text-text-secondary">{item.risk_score}</span>
        </div>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (item) => (
        <IncidentStatusBadge status={item.status} size="sm" />
      ),
    },
    {
      header: 'Owner',
      accessor: 'owner',
      render: () => (
        <span className="text-xs text-text-muted italic select-none">
          Unassigned
        </span>
      ),
    },
    {
      header: 'Created',
      accessor: 'created_at',
      render: (item) => (
        <span className="text-xs text-text-muted">
          {new Date(item.created_at).toLocaleString(undefined, {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      ),
    },
    {
      header: 'Updated',
      accessor: 'updated_at',
      render: () => (
        <span className="text-xs text-text-muted select-none">
          -
        </span>
      ),
    },
    {
      header: 'Actions',
      accessor: 'incident_id',
      render: (item) => (
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails(item.incident_id);
            }}
            className="py-1 px-2.5 text-xs"
          >
            Triage
          </Button>
          
          {user?.role === ROLES.ADMIN && (
            <Button
              variant="danger"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(item.incident_id);
              }}
              className="py-1 px-2.5 text-xs bg-red/10 border-red/20 text-red hover:bg-red/20 hover:text-text-primary"
            >
              Delete
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={incidents}
      isLoading={loading}
      emptyMessage="No Security Incidents Detected"
      emptySubMessage="Correlate logs or submit a new telemetry stream to generate alerts."
      onRowClick={(item) => onViewDetails(item.incident_id)}
    />
  );
}
