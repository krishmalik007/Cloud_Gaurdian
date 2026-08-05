import React from 'react';
import { Badge } from '../ui/Badge';

export default function ThreatRiskBadge({ severity = 'LOW' }) {
  const getVariant = (s) => {
    const norm = String(s).toUpperCase();
    if (norm === 'CRITICAL' || norm === 'HIGH') return 'danger';
    if (norm === 'MEDIUM') return 'warning';
    return 'success';
  };

  return (
    <Badge variant={getVariant(severity)} size="md" dot>
      {severity}
    </Badge>
  );
}
