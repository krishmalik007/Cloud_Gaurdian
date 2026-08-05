import React from 'react';
import { Badge } from '../ui/Badge';

export default function IncidentStatusBadge({ status = 'OPEN', size = 'md' }) {
  const getStatusVariant = (level) => {
    const l = String(level).toUpperCase();
    if (l === 'OPEN') return 'danger';
    if (l === 'INVESTIGATING') return 'warning';
    if (l === 'RESOLVED') return 'success';
    if (l === 'CLOSED') return 'muted';
    return 'info';
  };

  return (
    <Badge variant={getStatusVariant(status)} size={size}>
      {status}
    </Badge>
  );
}
