import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Table } from '../ui/Table';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { ROUTES } from '../../constants/routes';

export default function RecentIncidents({ incidents = [], loading = false }) {
  const navigate = useNavigate();

  const getSeverityVariant = (severity) => {
    const s = String(severity).toUpperCase();
    if (s === 'CRITICAL' || s === 'HIGH') return 'danger';
    if (s === 'MEDIUM') return 'warning';
    if (s === 'LOW') return 'info';
    return 'muted';
  };

  const getStatusVariant = (status) => {
    const s = String(status).toUpperCase();
    if (s === 'OPEN') return 'danger';
    if (s === 'INVESTIGATING') return 'warning';
    if (s === 'RESOLVED') return 'success';
    return 'muted';
  };

  const getProviderVariant = (provider) => {
    const p = String(provider).toUpperCase();
    if (p === 'AWS') return 'warning';
    if (p === 'AZURE') return 'info';
    if (p === 'GCP') return 'purple';
    return 'muted';
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
      header: 'Risk Level',
      accessor: 'risk_level',
      render: (item) => (
        <Badge variant={getSeverityVariant(item.risk_level)} size="sm" dot>
          {String(item.risk_level).toUpperCase()}
        </Badge>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (item) => (
        <Badge variant={getStatusVariant(item.status)} size="sm">
          {String(item.status).toUpperCase()}
        </Badge>
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
      header: 'Action',
      accessor: 'incident_id',
      render: (item) => (
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate(ROUTES.INCIDENT_DETAILS.replace(':id', item.incident_id))}
          className="text-xs py-1"
        >
          View Details
        </Button>
      ),
    },
  ];

  return (
    <div className="flex flex-col gap-4 text-left w-full">
      <div className="flex items-center justify-between select-none">
        <div className="flex flex-col gap-0.5">
          <h3 className="text-sm font-semibold text-text-primary tracking-tight">Recent Correlated Alerts</h3>
          <p className="text-xs text-text-muted">Latest security events analyzed and indexed into OpenSearch.</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate(ROUTES.INCIDENTS)}
        >
          View All Alerts
        </Button>
      </div>

      <Table
        columns={columns}
        data={incidents}
        isLoading={loading}
        emptyMessage="No Recent Incidents Found"
        emptySubMessage="Correlate logs or submit a new telemetry stream to generate alerts."
        onRowClick={(item) => navigate(ROUTES.INCIDENT_DETAILS.replace(':id', item.incident_id))}
      />
    </div>
  );
}
