import React from 'react';
import { Table } from '../ui/Table';
import { Button } from '../ui/Button';
import AuditActionBadge from './AuditActionBadge';
import AuditStatusBadge from './AuditStatusBadge';

export default function AuditTable({
  logs = [],
  loading = false,
  onViewDetails,
}) {
  const getRole = (name) => {
    if (name === 'admin' || name === 'krish') return 'Admin';
    return 'Analyst';
  };

  const columns = [
    {
      header: 'Audit ID',
      accessor: 'audit_id',
      render: (item) => (
        <span className="font-mono text-xs font-semibold text-text-primary select-all">
          {item.audit_id}
        </span>
      ),
    },
    {
      header: 'Timestamp',
      accessor: 'timestamp',
      render: (item) => (
        <span className="text-xs text-text-muted">
          {new Date(item.timestamp).toLocaleString(undefined, {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      ),
    },
    {
      header: 'User',
      accessor: 'username',
      render: (item) => (
        <span className="text-xs font-semibold text-text-secondary">
          {item.username}
        </span>
      ),
    },
    {
      header: 'Role',
      accessor: 'username',
      render: (item) => (
        <span className="text-xs text-text-muted">
          {getRole(item.username)}
        </span>
      ),
    },
    {
      header: 'Action',
      accessor: 'action',
      render: (item) => (
        <AuditActionBadge action={item.action} size="sm" />
      ),
    },
    {
      header: 'Resource',
      accessor: 'resource',
      render: (item) => (
        <span className="text-xs text-text-secondary font-mono truncate max-w-[150px] block" title={item.resource}>
          {item.resource}
        </span>
      ),
    },
    {
      header: 'Status',
      accessor: 'status',
      render: (item) => (
        <AuditStatusBadge status={item.status} size="sm" />
      ),
    },
    {
      header: 'IP Address',
      accessor: 'ip_address',
      render: (item) => (
        <span className="font-mono text-xs text-text-muted">
          {item.ip_address || '-'}
        </span>
      ),
    },
    {
      header: 'Actions',
      accessor: 'audit_id',
      render: (item) => (
        <Button
          variant="outline"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            onViewDetails(item.audit_id);
          }}
          className="py-1 px-2.5 text-xs"
        >
          Details
        </Button>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={logs}
      isLoading={loading}
      emptyMessage="No Audit Logs Found"
      emptySubMessage="Operational and security activities will be indexed automatically."
      onRowClick={(item) => onViewDetails(item.audit_id)}
    />
  );
}
