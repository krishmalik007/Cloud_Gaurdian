import React, { useState } from 'react';
import { useAuditLogs } from '../../hooks/useAudit';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { Pagination } from '../../components/ui/Pagination';
import { toast } from 'react-toastify';

// Components
import AuditStats from '../../components/audit/AuditStats';
import AuditToolbar from '../../components/audit/AuditToolbar';
import AuditTable from '../../components/audit/AuditTable';
import AuditDrawer from '../../components/audit/AuditDrawer';
import AuditEmptyState from '../../components/audit/AuditEmptyState';
import AuditLoading from '../../components/audit/AuditLoading';
import AuditError from '../../components/audit/AuditError';

export default function AuditLogsPage() {
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({
    action: null,
    status: null,
    dateOrder: 'newest',
  });
  const [page, setPage] = useState(1);
  const [size] = useState(10);

  const [selectedAuditId, setSelectedAuditId] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // Load audit logs using React Query hook
  const { data, isLoading, isFetching, isError, error, refetch } = useAuditLogs();

  const handleExportLogs = () => {
    toast.info('Exporting logs context is not supported by the current API framework.');
  };

  const handleViewDetails = (auditId) => {
    setSelectedAuditId(auditId);
    setIsDrawerOpen(true);
  };

  // Extract raw log list
  const rawLogs = data?.audit_logs || [];

  // Filter logs locally
  const filteredLogs = rawLogs.filter((log) => {
    const matchesSearch =
      !search ||
      String(log.audit_id).toLowerCase().includes(search.toLowerCase()) ||
      String(log.username).toLowerCase().includes(search.toLowerCase()) ||
      String(log.action).toLowerCase().includes(search.toLowerCase()) ||
      String(log.resource).toLowerCase().includes(search.toLowerCase());

    const matchesAction = !filters.action || log.action === filters.action;
    const matchesStatus = !filters.status || log.status === filters.status;

    return matchesSearch && matchesAction && matchesStatus;
  });

  // Sort logs locally
  const sortedLogs = [...filteredLogs].sort((a, b) => {
    const timeA = new Date(a.timestamp).getTime();
    const timeB = new Date(b.timestamp).getTime();
    return filters.dateOrder === 'newest' ? timeB - timeA : timeA - timeB;
  });

  // Paginate logs locally
  const paginatedLogs = sortedLogs.slice((page - 1) * size, page * size);

  return (
    <div className="flex flex-col gap-6 w-full animate-fade-in text-left">
      <PageHeader
        title="Operational Audit Logs"
        subtitle="Chronological and tamper-evident event trails mapping administrative security tasks."
        action={
          <Button variant="outline" size="sm" onClick={handleExportLogs}>
            Export Audit Trails
          </Button>
        }
      />

      {/* Stats Cards */}
      <AuditStats logs={rawLogs} loading={isLoading} />

      {/* Search and Filters Toolbar */}
      <AuditToolbar
        search={search}
        onSearchChange={(val) => { setSearch(val); setPage(1); }}
        filters={filters}
        onFilterChange={(newFilters) => { setFilters(newFilters); setPage(1); }}
        onRefresh={refetch}
        isRefreshing={isFetching}
      />

      {/* Main Audit Logs Grid */}
      {isLoading ? (
        <AuditLoading />
      ) : isError ? (
        <AuditError error={error} onRetry={refetch} />
      ) : sortedLogs.length === 0 ? (
        <AuditEmptyState onRefresh={refetch} />
      ) : (
        <div className="flex flex-col w-full">
          <AuditTable
            logs={paginatedLogs}
            loading={isLoading}
            onViewDetails={handleViewDetails}
          />

          <Pagination
            currentPage={page}
            totalPages={Math.ceil(sortedLogs.length / size)}
            totalItems={sortedLogs.length}
            itemsPerPage={size}
            onPageChange={setPage}
          />
        </div>
      )}

      {/* Detailed Slide-out Drawer */}
      <AuditDrawer
        isOpen={isDrawerOpen}
        onClose={() => {
          setIsDrawerOpen(false);
          setSelectedAuditId(null);
        }}
        auditId={selectedAuditId}
      />
    </div>
  );
}
