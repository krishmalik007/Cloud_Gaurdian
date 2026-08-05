import React from 'react';
import { Badge } from '../ui/Badge';

export default function IncidentSeverityBadge({ severity = 'INFO', size = 'md' }) {
  const getSeverityVariant = (level) => {
    const l = String(level).toUpperCase();
    if (l === 'CRITICAL') return 'danger';
    if (l === 'HIGH') return 'danger';
    if (l === 'MEDIUM') return 'warning';
    if (l === 'LOW') return 'info';
    return 'muted';
  };

  return (
    <Badge variant={getSeverityVariant(severity)} size={size} dot>
      {severity}
    </Badge>
  );
}
