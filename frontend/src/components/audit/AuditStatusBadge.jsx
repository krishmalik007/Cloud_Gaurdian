import React from 'react';
import { Badge } from '../ui/Badge';

export default function AuditStatusBadge({ status = 'SUCCESS', size = 'md' }) {
  const getStatusVariant = (stat) => {
    const s = String(stat).toUpperCase();
    if (s === 'SUCCESS') return 'success';
    if (s === 'FAILED') return 'danger';
    return 'muted';
  };

  return (
    <Badge variant={getStatusVariant(status)} size={size} dot={status === 'FAILED'}>
      {status}
    </Badge>
  );
}
