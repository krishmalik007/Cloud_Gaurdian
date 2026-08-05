import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useIncidentsSearch, useDeleteIncident } from '../../hooks/useIncidents';
import { useAuth } from '../../context/AuthContext';
import { ROLES } from '../../constants/roles';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Pagination } from '../../components/ui/Pagination';
import { toast } from 'react-toastify';
import API from '../../services/api';

// Components
import IncidentToolbar from '../../components/incidents/IncidentToolbar';
import IncidentTable from '../../components/incidents/IncidentTable';
import IncidentDrawer from '../../components/incidents/IncidentDrawer';
import DeleteIncidentDialog from '../../components/incidents/DeleteIncidentDialog';
import EmptyIncident from '../../components/incidents/EmptyIncident';
import IncidentSeverityBadge from '../../components/incidents/IncidentSeverityBadge';
import IncidentStatusBadge from '../../components/incidents/IncidentStatusBadge';

export default function IncidentPage() {
  const { user } = useAuth();
  
  // State for search and filters
  const [filters, setFilters] = useState({
    provider: null,
    risk_level: null,
    status: null,
    username: null,
    page: 1,
    size: 10,
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  // Drawer and Delete dialog states
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Queries & Mutations
  const { data: searchResult, isLoading, isFetching, refetch, isError } = useIncidentsSearch(filters);
  const deleteMutation = useDeleteIncident();

  // Load summary statistics for the headers
  const { data: summaryData, isLoading: loadingSummary } = useQuery({
    queryKey: ['dashboard', 'summary-statistics'],
    queryFn: async () => {
      const response = await API.get('/dashboard/summary');
      return response.data;
    },
  });

  // Load risk distribution for exact counts
  const { data: riskData } = useQuery({
    queryKey: ['dashboard', 'risk-distribution-stats'],
    queryFn: async () => {
      const response = await API.get('/dashboard/risk-distribution');
      return response.data;
    },
  });

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({
      ...prev,
      page: newPage,
    }));
  };

  const handleViewDetails = (incidentId) => {
    setSelectedIncidentId(incidentId);
    setIsDrawerOpen(true);
  };

  const handleDeleteTrigger = (incidentId) => {
    setDeleteTargetId(incidentId);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTargetId) return;
    try {
      await deleteMutation.mutateAsync(deleteTargetId);
      toast.success('Incident deleted successfully.');
      setIsDeleteDialogOpen(false);
      setDeleteTargetId(null);
    } catch (err) {
      toast.error('Failed to delete incident: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Calculate statistics
  const totalCount = summaryData?.total_incidents || 0;
  const openCount = summaryData?.open_incidents || 0;
  const resolvedCount = summaryData?.closed_incidents || 0;
  const highCount = summaryData?.high_risk || 0;
  
  const criticalCount = riskData?.find(
    (r) => String(r.risk_level).toUpperCase() === 'CRITICAL'
  )?.count || 0;

  return (
    <div className="flex flex-col gap-6 w-full animate-fade-in text-left">
      <PageHeader
        title="Incident Operations Center"
        subtitle="Perform unified triage, threat correlation, and lifecycle audits across connected cloud environments."
      />

      {/* Mini Stats Summary Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 select-none">
        <Card title="Total" subtitle="All incidents" className="!p-4 bg-surface/30">
          <span className="text-xl font-extrabold text-text-primary block mt-1">
            {loadingSummary ? '...' : totalCount}
          </span>
        </Card>
        <Card title="Critical" subtitle="Highest threat level" className="!p-4 bg-surface/30 border-l-2 border-l-red">
          <span className="text-xl font-extrabold text-red block mt-1">
            {loadingSummary ? '...' : criticalCount}
          </span>
        </Card>
        <Card title="High" subtitle="Aggressive threat" className="!p-4 bg-surface/30 border-l-2 border-l-orange">
          <span className="text-xl font-extrabold text-orange block mt-1">
            {loadingSummary ? '...' : highCount}
          </span>
        </Card>
        <Card title="Open" subtitle="Unresolved alerts" className="!p-4 bg-surface/30 border-l-2 border-l-red">
          <span className="text-xl font-extrabold text-red block mt-1">
            {loadingSummary ? '...' : openCount}
          </span>
        </Card>
        <Card title="Investigating" subtitle="Under analysis" className="!p-4 bg-surface/30 border-l-2 border-l-orange">
          <span className="text-xl font-extrabold text-orange block mt-1">
            {/* Investigating state is derived from Open incidents without Closed status */}
            {loadingSummary ? '...' : Math.max(0, openCount - criticalCount)}
          </span>
        </Card>
        <Card title="Resolved" subtitle="Remediated issues" className="!p-4 bg-surface/30 border-l-2 border-l-green">
          <span className="text-xl font-extrabold text-green block mt-1">
            {loadingSummary ? '...' : resolvedCount}
          </span>
        </Card>
      </div>

      {/* Incident Toolbar */}
      <IncidentToolbar
        filters={filters}
        onFilterChange={setFilters}
        onRefresh={refetch}
        isRefreshing={isFetching}
      />

      {/* Incident Table */}
      {isError ? (
        <div className="py-12 text-center text-red font-medium border border-border-color bg-surface/20 rounded-xl">
          Error: Failed to connect to log database. Please verify OpenSearch connection.
        </div>
      ) : !isLoading && (!searchResult?.incidents || searchResult.incidents.length === 0) ? (
        <EmptyIncident onRefresh={refetch} />
      ) : (
        <div className="flex flex-col w-full">
          <IncidentTable
            incidents={searchResult?.incidents || []}
            loading={isLoading}
            onViewDetails={handleViewDetails}
            onDelete={handleDeleteTrigger}
          />
          
          <Pagination
            currentPage={filters.page}
            totalPages={Math.ceil((searchResult?.total || 0) / filters.size)}
            totalItems={searchResult?.total || 0}
            itemsPerPage={filters.size}
            onPageChange={handlePageChange}
          />
        </div>
      )}

      {/* Detail Slide-out Drawer */}
      <IncidentDrawer
        isOpen={isDrawerOpen}
        onClose={() => {
          setIsDrawerOpen(false);
          setSelectedIncidentId(null);
        }}
        incidentId={selectedIncidentId}
      />

      {/* Delete Confirmation Modal */}
      {user?.role === ROLES.ADMIN && (
        <DeleteIncidentDialog
          isOpen={isDeleteDialogOpen}
          onClose={() => {
            setIsDeleteDialogOpen(false);
            setDeleteTargetId(null);
          }}
          onConfirm={handleDeleteConfirm}
          incidentId={deleteTargetId}
          isDeleting={deleteMutation.isPending}
        />
      )}
    </div>
  );
}
