import React from 'react';
import { Table } from '../ui/Table';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { useAuth } from '../../context/AuthContext';
import { ROLES } from '../../constants/roles';

export default function IOCTable({
  iocs = [],
  loading = false,
  onToggleStatus,
  onEdit,
  onDelete,
}) {
  const { user } = useAuth();

  const getSeverityVariant = (severity) => {
    const s = String(severity).toUpperCase();
    if (s === 'CRITICAL' || s === 'HIGH') return 'danger';
    if (s === 'MEDIUM') return 'warning';
    if (s === 'LOW') return 'info';
    return 'muted';
  };

  const getIndicatorVariant = (type) => {
    const t = String(type).toUpperCase();
    if (t === 'IP') return 'warning';
    if (t === 'DOMAIN') return 'info';
    if (t === 'USERNAME') return 'purple';
    return 'muted';
  };

  const columns = [
    {
      header: 'Indicator Type',
      accessor: 'type',
      render: (item) => (
        <Badge variant={getIndicatorVariant(item.type)} size="sm">
          {item.type}
        </Badge>
      ),
    },
    {
      header: 'Pattern Value',
      accessor: 'value',
      render: (item) => (
        <span className="font-mono text-xs font-semibold text-text-primary select-all">
          {item.value}
        </span>
      ),
    },
    {
      header: 'Risk Severity',
      accessor: 'severity',
      render: (item) => (
        <Badge variant={getSeverityVariant(item.severity)} size="sm" dot>
          {item.severity}
        </Badge>
      ),
    },
    {
      header: 'Feed Source',
      accessor: 'source',
      render: (item) => (
        <span className="text-xs text-text-secondary select-none">
          {item.source}
        </span>
      ),
    },
    {
      header: 'Triage Check',
      accessor: 'enabled',
      render: (item) => (
        <div className="flex items-center gap-2">
          {/* Custom Toggle Switch */}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              if (user?.role === ROLES.ADMIN) {
                onToggleStatus(item.ioc_id, !item.enabled);
              }
            }}
            disabled={user?.role !== ROLES.ADMIN}
            className={`relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-1 focus:ring-primary-blue focus:ring-offset-1 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed ${
              item.enabled ? 'bg-primary-blue' : 'bg-background border-border-color'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-text-primary shadow-lg ring-0 transition duration-200 ease-in-out ${
                item.enabled ? 'translate-x-4' : 'translate-x-0'
              }`}
            />
          </button>
          <span className="text-[10px] font-bold text-text-secondary uppercase select-none">
            {item.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
      ),
    },
    {
      header: 'Created Time',
      accessor: 'created_at',
      render: (item) => (
        <span className="text-xs text-text-muted">
          {new Date(item.created_at).toLocaleString()}
        </span>
      ),
    },
    {
      header: 'Actions',
      accessor: 'ioc_id',
      render: (item) => (
        <div className="flex items-center gap-2">
          {user?.role === ROLES.ADMIN ? (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(item);
                }}
                className="py-1 px-2.5 text-xs"
              >
                Configure
              </Button>
              
              <Button
                variant="danger"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(item);
                }}
                className="py-1 px-2.5 text-xs bg-red/10 border-red/20 text-red hover:bg-red/20 hover:text-text-primary"
              >
                Delete
              </Button>
            </>
          ) : (
            <span className="text-xs text-text-muted select-none">
              Read-Only Clearance
            </span>
          )}
        </div>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={iocs}
      isLoading={loading}
      emptyMessage="No Watchlist Indicators Found"
      emptySubMessage="Register an indicator of compromise to verify raw log streams automatically."
    />
  );
}
