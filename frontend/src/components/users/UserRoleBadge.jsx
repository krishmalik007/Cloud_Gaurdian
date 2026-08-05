import React from 'react';
import { Badge } from '../ui/Badge';

export default function UserRoleBadge({ role = 'ANALYST', size = 'md' }) {
  const isAdmin = String(role).toUpperCase() === 'ADMIN';

  return (
    <Badge variant={isAdmin ? 'danger' : 'info'} size={size}>
      {isAdmin ? 'Administrator' : 'Analyst'}
    </Badge>
  );
}
