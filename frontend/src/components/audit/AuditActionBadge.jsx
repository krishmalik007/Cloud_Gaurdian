import React from 'react';
import { Badge } from '../ui/Badge';

export default function AuditActionBadge({ action = '', size = 'md' }) {
  const getActionVariant = (act) => {
    const a = String(act).toUpperCase();
    if (a.includes('DELETE')) return 'danger';
    if (a.includes('CREATE') || a.includes('UPDATE')) return 'info';
    if (a === 'LOGIN' || a === 'REGISTER') return 'success';
    if (a.includes('UPLOAD')) return 'warning';
    return 'muted';
  };

  return (
    <Badge variant={getActionVariant(action)} size={size}>
      {action}
    </Badge>
  );
}
