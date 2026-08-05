import React, { useState } from 'react';
import { useUsersList, useUpdateRole, useUpdateStatus, useDeleteUser } from '../../hooks/useUsers';
import { useAuth } from '../../context/AuthContext';
import { PageHeader } from '../../components/layout/PageHeader';
import { Pagination } from '../../components/ui/Pagination';
import { toast } from 'react-toastify';

// Components
import UsersStats from '../../components/users/UsersStats';
import UsersToolbar from '../../components/users/UsersToolbar';
import UsersTable from '../../components/users/UsersTable';
import UserDrawer from '../../components/users/UserDrawer';
import UsersEmptyState from '../../components/users/UsersEmptyState';
import UsersLoading from '../../components/users/UsersLoading';
import UsersError from '../../components/users/UsersError';

// Dialogs
import RoleUpdateDialog from '../../components/users/RoleUpdateDialog';
import StatusUpdateDialog from '../../components/users/StatusUpdateDialog';
import DeleteUserDialog from '../../components/users/DeleteUserDialog';

export default function UsersPage() {
  const { user: currentUser } = useAuth();

  // Search & Filters
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({
    role: null,
    enabled: null,
    order: 'newest',
  });
  const [page, setPage] = useState(1);
  const [size] = useState(10);

  // Drawer / Modals Toggles
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const [activeUserTarget, setActiveUserTarget] = useState(null);
  const [isRoleOpen, setIsRoleOpen] = useState(false);
  const [isStatusOpen, setIsStatusOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  // Queries & Mutations
  const { data, isLoading, isFetching, isError, error, refetch } = useUsersList();
  const roleMutation = useUpdateRole();
  const statusMutation = useUpdateStatus();
  const deleteMutation = useDeleteUser();

  const handleProfileView = (userId) => {
    setSelectedUserId(userId);
    setIsDrawerOpen(true);
  };

  const handleRoleTrigger = (user) => {
    setActiveUserTarget(user);
    setIsRoleOpen(true);
  };

  const handleRoleConfirm = async () => {
    if (!activeUserTarget) return;
    const targetRole = activeUserTarget.role === 'ADMIN' ? 'ANALYST' : 'ADMIN';
    try {
      await roleMutation.mutateAsync({
        userId: activeUserTarget.user_id,
        role: targetRole,
      });
      toast.success(`User role updated to ${targetRole} successfully.`);
      setIsRoleOpen(false);
      setActiveUserTarget(null);
    } catch (err) {
      toast.error('Failed to change role: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleStatusTrigger = (user) => {
    setActiveUserTarget(user);
    setIsStatusOpen(true);
  };

  const handleStatusConfirm = async () => {
    if (!activeUserTarget) return;
    const targetEnabled = !activeUserTarget.enabled;
    try {
      await statusMutation.mutateAsync({
        userId: activeUserTarget.user_id,
        enabled: targetEnabled,
      });
      toast.success(`Account ${targetEnabled ? 'activated' : 'locked'} successfully.`);
      setIsStatusOpen(false);
      setActiveUserTarget(null);
    } catch (err) {
      toast.error('Failed to change account status: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeleteTrigger = (user) => {
    // Prevent deletion of self
    if (user.user_id === currentUser?.user_id) {
      toast.error('Self-deletion is blocked. Administrative safety measures active.');
      return;
    }
    setActiveUserTarget(user);
    setIsDeleteOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!activeUserTarget) return;
    try {
      await deleteMutation.mutateAsync(activeUserTarget.user_id);
      toast.success('Personnel profile removed successfully.');
      setIsDeleteOpen(false);
      setActiveUserTarget(null);
    } catch (err) {
      toast.error('Failed to delete account: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Local Filtering
  const rawUsers = data?.users || [];
  
  const filteredUsers = rawUsers.filter((u) => {
    const matchesSearch =
      !search ||
      String(u.username).toLowerCase().includes(search.toLowerCase()) ||
      String(u.user_id).toLowerCase().includes(search.toLowerCase()) ||
      String(u.email || '').toLowerCase().includes(search.toLowerCase());

    const matchesRole = !filters.role || u.role === filters.role;
    const matchesEnabled = filters.enabled === null || u.enabled === filters.enabled;

    return matchesSearch && matchesRole && matchesEnabled;
  });

  // Local Sorting
  const sortedUsers = [...filteredUsers].sort((a, b) => {
    const timeA = new Date(a.created_at).getTime();
    const timeB = new Date(b.created_at).getTime();
    return filters.order === 'newest' ? timeB - timeA : timeA - timeB;
  });

  // Local Pagination
  const paginatedUsers = sortedUsers.slice((page - 1) * size, page * size);

  return (
    <div className="flex flex-col gap-6 w-full animate-fade-in text-left">
      <PageHeader
        title="User Administration"
        subtitle="Manage analyst permissions, security roles, and active session status controls."
      />

      {/* Stats row */}
      <UsersStats users={rawUsers} loading={isLoading} />

      {/* Search & Filters Toolbar */}
      <UsersToolbar
        search={search}
        onSearchChange={(val) => { setSearch(val); setPage(1); }}
        filters={filters}
        onFilterChange={(newFilters) => { setFilters(newFilters); setPage(1); }}
        onRefresh={refetch}
        isRefreshing={isFetching}
      />

      {/* Main Grid */}
      {isLoading ? (
        <UsersLoading />
      ) : isError ? (
        <UsersError error={error} onRetry={refetch} />
      ) : sortedUsers.length === 0 ? (
        <UsersEmptyState onRefresh={refetch} />
      ) : (
        <div className="flex flex-col w-full">
          <UsersTable
            users={paginatedUsers}
            loading={isLoading}
            onView={handleProfileView}
            onChangeRole={handleRoleTrigger}
            onToggleStatus={handleStatusTrigger}
            onDelete={handleDeleteTrigger}
          />

          <Pagination
            currentPage={page}
            totalPages={Math.ceil(sortedUsers.length / size)}
            totalItems={sortedUsers.length}
            itemsPerPage={size}
            onPageChange={setPage}
          />
        </div>
      )}

      {/* User drawer profiles */}
      <UserDrawer
        isOpen={isDrawerOpen}
        onClose={() => {
          setIsDrawerOpen(false);
          setSelectedUserId(null);
        }}
        userId={selectedUserId}
      />

      {/* Role Confirmation */}
      {isRoleOpen && activeUserTarget && (
        <RoleUpdateDialog
          isOpen={isRoleOpen}
          onClose={() => { setIsRoleOpen(false); setActiveUserTarget(null); }}
          onConfirm={handleRoleConfirm}
          username={activeUserTarget.username}
          targetRole={activeUserTarget.role === 'ADMIN' ? 'ANALYST' : 'ADMIN'}
          isUpdating={roleMutation.isPending}
        />
      )}

      {/* Status Confirmation */}
      {isStatusOpen && activeUserTarget && (
        <StatusUpdateDialog
          isOpen={isStatusOpen}
          onClose={() => { setIsStatusOpen(false); setActiveUserTarget(null); }}
          onConfirm={handleStatusConfirm}
          username={activeUserTarget.username}
          targetEnabled={!activeUserTarget.enabled}
          isUpdating={statusMutation.isPending}
        />
      )}

      {/* Delete Confirmation */}
      {isDeleteOpen && activeUserTarget && (
        <DeleteUserDialog
          isOpen={isDeleteOpen}
          onClose={() => { setIsDeleteOpen(false); setActiveUserTarget(null); }}
          onConfirm={handleDeleteConfirm}
          username={activeUserTarget.username}
          isDeleting={deleteMutation.isPending}
        />
      )}
    </div>
  );
}
