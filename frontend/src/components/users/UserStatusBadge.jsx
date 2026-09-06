import React from 'react';
import { Badge } from '../ui/Badge';

export default function UserStatusBadge({ enabled = true, size = 'md' }) {
  return (
    <Badge variant={enabled ? 'success' : 'muted'} size={size} dot={!enabled}>
      {enabled ? 'Account: Active' : 'Account: Disabled'}
    </Badge>
  );
}
