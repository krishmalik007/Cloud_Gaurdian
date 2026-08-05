import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useIOCs, useCreateIOC, useUpdateIOC, useDeleteIOC } from '../../hooks/useIOC';
import { useAuth } from '../../context/AuthContext';
import { ROLES } from '../../constants/roles';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { toast } from 'react-toastify';

// Components
import IOCStats from '../../components/ioc/IOCStats';
import IOCFilters from '../../components/ioc/IOCFilters';
import IOCTable from '../../components/ioc/IOCTable';
import CreateIOCModal from '../../components/ioc/CreateIOCModal';
import EditIOCDrawer from '../../components/ioc/EditIOCDrawer';
import DeleteIOCDialog from '../../components/ioc/DeleteIOCDialog';

export default function IOCManagement() {
  const { user } = useAuth();

  // Filter States
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({
    type: null,
    severity: null,
    enabled: null,
  });

  // Modal / Drawer Toggles
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedIOC, setSelectedIOC] = useState(null);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  // Queries & Mutations
  const { data: iocs = [], isLoading, isError, refetch } = useIOCs();
  const createMutation = useCreateIOC();
  const updateMutation = useUpdateIOC();
  const deleteMutation = useDeleteIOC();

  // Local filtering & search logic
  const filteredIOCs = iocs.filter((ioc) => {
    const matchesSearch =
      !search ||
      String(ioc.value).toLowerCase().includes(search.toLowerCase()) ||
      String(ioc.description || '').toLowerCase().includes(search.toLowerCase());

    const matchesType = !filters.type || ioc.type === filters.type;
    
    const matchesSeverity =
      !filters.severity || ioc.severity === filters.severity;

    const matchesEnabled =
      filters.enabled === null || ioc.enabled === filters.enabled;

    return matchesSearch && matchesType && matchesSeverity && matchesEnabled;
  });

  // Action handlers
  const handleCreateSubmit = async (data) => {
    try {
      await createMutation.mutateAsync(data);
      toast.success('Indicator created successfully.');
      setIsCreateOpen(false);
    } catch (err) {
      toast.error('Failed to create indicator: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleToggleStatus = async (iocId, newEnabled) => {
    try {
      await updateMutation.mutateAsync({
        iocId,
        updates: { enabled: newEnabled },
      });
      toast.success(`Indicator ${newEnabled ? 'enabled' : 'disabled'} successfully.`);
    } catch (err) {
      toast.error('Failed to update status: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleEditTrigger = (ioc) => {
    setSelectedIOC(ioc);
    setIsEditOpen(true);
  };

  const handleEditSubmit = async (updates) => {
    if (!selectedIOC) return;
    try {
      await updateMutation.mutateAsync({
        iocId: selectedIOC.ioc_id,
        updates,
      });
      toast.success('Indicator updated successfully.');
      setIsEditOpen(false);
      setSelectedIOC(null);
    } catch (err) {
      toast.error('Failed to update indicator: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeleteTrigger = (ioc) => {
    setDeleteTarget(ioc);
    setIsDeleteOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    try {
      await deleteMutation.mutateAsync(deleteTarget.ioc_id);
      toast.success('Indicator removed successfully.');
      setIsDeleteOpen(false);
      setDeleteTarget(null);
    } catch (err) {
      toast.error('Failed to remove indicator: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="flex flex-col gap-6 w-full animate-fade-in text-left">
      <PageHeader
        title="IOC Threat Database"
        subtitle="Manage Indicators of Compromise (IPs, domains, and users) checked by the correlation engine."
        action={
          user?.role === ROLES.ADMIN ? (
            <Button variant="primary" size="sm" onClick={() => setIsCreateOpen(true)}>
              Register Indicator
            </Button>
          ) : null
        }
      />

      {/* Statistics Cards */}
      <IOCStats iocs={iocs} loading={isLoading} />

      {/* Toolbar Filters */}
      <IOCFilters
        search={search}
        onSearchChange={setSearch}
        filters={filters}
        onFilterChange={setFilters}
      />

      {/* Data Table */}
      {isError ? (
        <div className="py-12 text-center text-red font-semibold border border-border-color bg-surface/20 rounded-xl">
          Error: Failed to fetch indicator feeds. Verify backend connectivity.
        </div>
      ) : (
        <IOCTable
          iocs={filteredIOCs}
          loading={isLoading}
          onToggleStatus={handleToggleStatus}
          onEdit={handleEditTrigger}
          onDelete={handleDeleteTrigger}
        />
      )}

      {/* Create Modal */}
      {isCreateOpen && (
        <CreateIOCModal
          isOpen={isCreateOpen}
          onClose={() => setIsCreateOpen(false)}
          onSubmit={handleCreateSubmit}
          isSubmitting={createMutation.isPending}
        />
      )}

      {/* Edit Drawer */}
      {isEditOpen && (
        <EditIOCDrawer
          isOpen={isEditOpen}
          onClose={() => {
            setIsEditOpen(false);
            setSelectedIOC(null);
          }}
          ioc={selectedIOC}
          onSubmit={handleEditSubmit}
          isSubmitting={updateMutation.isPending}
        />
      )}

      {/* Delete Confirmation */}
      {isDeleteOpen && (
        <DeleteIOCDialog
          isOpen={isDeleteOpen}
          onClose={() => {
            setIsDeleteOpen(false);
            setDeleteTarget(null);
          }}
          onConfirm={handleDeleteConfirm}
          value={deleteTarget?.value}
          isDeleting={deleteMutation.isPending}
        />
      )}
    </div>
  );
}
