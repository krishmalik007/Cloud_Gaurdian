import React from 'react';
import { Table } from '../ui/Table';
import { Button } from '../ui/Button';
import { Avatar } from '../ui/Avatar';
import UserRoleBadge from './UserRoleBadge';
import UserStatusBadge from './UserStatusBadge';
import { useAuth } from '../../context/AuthContext';

export default function UsersTable({
  users = [],
  loading = false,
  onView,
  onChangeRole,
  onToggleStatus,
  onDelete,
}) {
  const { user: currentUser } = useAuth();

  const columns = [
    {
      header: 'User ID',
      accessor: 'user_id',
      render: (item) => (
        <span className="font-mono text-xs font-semibold text-text-primary select-all">
          {item.user_id}
        </span>
      ),
    },
    {
      header: 'Username',
      accessor: 'username',
      render: (item) => (
        <div className="flex items-center gap-2.5 select-none">
          <Avatar name={item.username} size="sm" />
          <span className="text-xs font-bold text-text-primary">{item.username}</span>
        </div>
      ),
    },
    {
      header: 'Email',
      accessor: 'email',
      render: (item) => (
        <span className="text-xs text-text-secondary select-all">{item.email}</span>
      ),
    },
    {
      header: 'Role',
      accessor: 'role',
      render: (item) => (
        <UserRoleBadge role={item.role} size="sm" />
      ),
    },
    {
      header: 'Status',
      accessor: 'enabled',
      render: (item) => (
        <UserStatusBadge enabled={item.enabled} size="sm" />
      ),
    },
    {
      header: 'Created At',
      accessor: 'created_at',
      render: (item) => (
        <span className="text-xs text-text-muted">
          {new Date(item.created_at).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          })}
        </span>
      ),
    },
    {
      header: 'Actions',
      accessor: 'user_id',
      render: (item) => (
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onView(item.user_id);
            }}
            className="py-1 px-2 text-xs"
          >
            Profile
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onChangeRole(item);
            }}
            className="py-1 px-2 text-xs"
          >
            Role
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onToggleStatus(item);
            }}
            className={`py-1 px-2 text-xs ${
              item.enabled
                ? 'text-warning border-warning/20 hover:bg-warning/10'
                : 'text-green border-green/20 hover:bg-green/10'
            }`}
          >
            {item.enabled ? 'Lock' : 'Unlock'}
          </Button>

          <Button
            variant="danger"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(item);
            }}
            className="py-1 px-2 text-xs bg-red/10 border-red/20 text-red hover:bg-red/20 hover:text-text-primary"
          >
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={users}
      isLoading={loading}
      emptyMessage="No Platform Users Registered"
      emptySubMessage="Credentials and role registries will be indexed automatically."
      onRowClick={(item) => onView(item.user_id)}
    />
  );
}
