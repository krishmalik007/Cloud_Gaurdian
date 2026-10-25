import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useIncidentsSearch, useDeleteIncident } from '../../hooks/useIncidents';
import { useEventsSearch, useEventStats } from '../../hooks/useEvents';
import { useAuth } from '../../context/AuthContext';
import { ROLES } from '../../constants/roles';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Pagination } from '../../components/ui/Pagination';
import { toast } from 'react-toastify';
import { useDashboardSummary, useDashboardRiskDistribution } from '../../hooks/useDashboard';

// Incident Components
import IncidentToolbar from '../../components/incidents/IncidentToolbar';
import IncidentTable from '../../components/incidents/IncidentTable';
import IncidentDrawer from '../../components/incidents/IncidentDrawer';
import DeleteIncidentDialog from '../../components/incidents/DeleteIncidentDialog';
import EmptyIncident from '../../components/incidents/EmptyIncident';

// Events Components
import EventsToolbar from '../../components/events/EventsToolbar';
import EventsTable from '../../components/events/EventsTable';
import EventDetailDrawer from '../../components/events/EventDetailDrawer';
import EmptyEvents from '../../components/events/EmptyEvents';

// Icons
import { RiAlertLine, RiFileList3Line } from 'react-icons/ri';

export default function IncidentPage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') === 'events' ? 'events' : 'incidents';

  const handleTabChange = (tabName) => {
    setSearchParams(tabName === 'events' ? { tab: 'events' } : {});
  };

  // State for incident search and filters
  const [incidentFilters, setIncidentFilters] = useState(() => {
    let defaultStatus = null;
    let defaultRisk = null;
    try {
      const prefs = JSON.parse(localStorage.getItem('cg_settings_preferences') || '{}');
      if (prefs.defaultView === 'open') {
        defaultStatus = 'OPEN';
      } else if (prefs.defaultView === 'critical') {
        defaultRisk = 'HIGH,CRITICAL';
      }

      if (prefs.showLowRisk === false && !defaultRisk) {
        defaultRisk = 'MEDIUM,HIGH,CRITICAL';
      }
    } catch (e) {}

    return {
      provider: null,
      risk_level: defaultRisk,
      status: defaultStatus,
      username: null,
      page: 1,
      size: 10,
      sort_by: 'created_at',
      sort_order: 'desc',
    };
  });

  // State for events search and filters
  const [eventFilters, setEventFilters] = useState({
    provider: null,
    risk_level: null,
    status: null,
    username: null,
    search: null,
    is_incident: null,
    page: 1,
    size: 15,
    sort_by: 'timestamp',
    sort_order: 'desc',
  });

  // Drawer and Delete dialog states
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);
  const [isIncidentDrawerOpen, setIsIncidentDrawerOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // Event Inspector state
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isEventDrawerOpen, setIsEventDrawerOpen] = useState(false);

  // Queries for Incidents
  const {
    data: incidentSearchResult,
    isLoading: loadingIncidents,
    isFetching: fetchingIncidents,
    refetch: refetchIncidents,
    isError: errorIncidents,
  } = useIncidentsSearch(incidentFilters);
  const deleteMutation = useDeleteIncident();

  // Queries for Events
  const {
    data: eventSearchResult,
    isLoading: loadingEvents,
    isFetching: fetchingEvents,
    refetch: refetchEvents,
    isError: errorEvents,
  } = useEventsSearch(eventFilters);
  const { data: eventStats } = useEventStats();

  // Load summary statistics for the headers
  const { data: summaryData, isLoading: loadingSummary } = useDashboardSummary();
  const { data: riskData } = useDashboardRiskDistribution();

  const handleIncidentPageChange = (newPage) => {
    setIncidentFilters((prev) => ({ ...prev, page: newPage }));
  };

  const handleEventPageChange = (newPage) => {
    setEventFilters((prev) => ({ ...prev, page: newPage }));
  };

  const handleViewIncidentDetails = (incidentId) => {
    setSelectedIncidentId(incidentId);
    setIsIncidentDrawerOpen(true);
  };

  const handleViewEventDetails = (event) => {
    setSelectedEvent(event);
    setIsEventDrawerOpen(true);
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
  const totalEventsCount = eventStats?.total_events || summaryData?.total_events || 0;
  const totalIncidentCount = summaryData?.total_incidents || 0;
  const openCount = summaryData?.open_incidents || 0;
  const highCount = summaryData?.high_risk || 0;
  const criticalCount = riskData?.find(
    (r) => String(r.risk_level).toUpperCase() === 'CRITICAL'
  )?.count || 0;

  return (
    <div className="flex flex-col gap-6 w-full animate-fade-in text-left">
      <PageHeader
        title="Incident Operations & Cloud Log Telemetry"
        subtitle="Perform unified triage across correlated security incidents and search all ingested multi-region cloud audit records."
      />

      {/* Mini Stats Summary Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 select-none">
        <Card
          title="All Telemetry Logs"
          subtitle="OpenSearch events index"
          className="!p-4 bg-surface/30 border-l-2 border-l-primary-blue cursor-pointer hover:border-primary-blue/60 transition-colors"
          onClick={() => handleTabChange('events')}
        >
          <span className="text-xl font-extrabold text-primary-blue block mt-1">
            {loadingSummary ? '...' : totalEventsCount.toLocaleString()}
          </span>
        </Card>
        <Card
          title="Correlated Incidents"
          subtitle="Actionable security threats"
          className="!p-4 bg-surface/30 border-l-2 border-l-red cursor-pointer hover:border-red/60 transition-colors"
          onClick={() => handleTabChange('incidents')}
        >
          <span className="text-xl font-extrabold text-text-primary block mt-1">
            {loadingSummary ? '...' : totalIncidentCount}
          </span>
        </Card>
        <Card title="Critical Alerts" subtitle="Immediate response" className="!p-4 bg-surface/30 border-l-2 border-l-red">
          <span className="text-xl font-extrabold text-red block mt-1">
            {loadingSummary ? '...' : criticalCount}
          </span>
        </Card>
        <Card title="High Threat" subtitle="Elevated risk score" className="!p-4 bg-surface/30 border-l-2 border-l-orange">
          <span className="text-xl font-extrabold text-orange block mt-1">
            {loadingSummary ? '...' : highCount}
          </span>
        </Card>
        <Card title="Open Incidents" subtitle="Unresolved alerts" className="!p-4 bg-surface/30 border-l-2 border-l-green">
          <span className="text-xl font-extrabold text-green block mt-1">
            {loadingSummary ? '...' : openCount}
          </span>
        </Card>
      </div>

      {/* Tab Selector Header */}
      <div className="flex items-center gap-3 border-b border-border-color pb-1 select-none">
        <button
          onClick={() => handleTabChange('incidents')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
            activeTab === 'incidents'
              ? 'bg-primary-blue/15 text-primary-blue border border-primary-blue/30 shadow-sm'
              : 'text-text-secondary hover:text-text-primary hover:bg-surface/50 border border-transparent'
          }`}
        >
          <RiAlertLine className="w-4 h-4" />
          <span>Security Incidents</span>
          <span className="ml-1.5 px-2 py-0.5 text-[10px] rounded-full bg-surface border border-border-color text-text-muted">
            {incidentSearchResult?.total ?? totalIncidentCount}
          </span>
        </button>

        <button
          onClick={() => handleTabChange('events')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
            activeTab === 'events'
              ? 'bg-primary-blue/15 text-primary-blue border border-primary-blue/30 shadow-sm'
              : 'text-text-secondary hover:text-text-primary hover:bg-surface/50 border border-transparent'
          }`}
        >
          <RiFileList3Line className="w-4 h-4" />
          <span>All Ingested Cloud Events</span>
          <span className="ml-1.5 px-2 py-0.5 text-[10px] rounded-full bg-primary-blue/20 text-primary-blue font-mono">
            {eventSearchResult?.total ?? totalEventsCount}
          </span>
        </button>
      </div>

      {/* View: Incidents */}
      {activeTab === 'incidents' && (
        <div className="flex flex-col gap-6 w-full animate-fade-in">
          <IncidentToolbar
            filters={incidentFilters}
            onFilterChange={setIncidentFilters}
            onRefresh={refetchIncidents}
            isRefreshing={fetchingIncidents}
          />

          {errorIncidents ? (
            <div className="py-12 text-center text-red font-medium border border-border-color bg-surface/20 rounded-xl">
              Error: Failed to connect to incident database. Please verify OpenSearch connection.
            </div>
          ) : !loadingIncidents && (!incidentSearchResult?.incidents || incidentSearchResult.incidents.length === 0) ? (
            <EmptyIncident
              onRefresh={refetchIncidents}
              onSwitchToEvents={() => handleTabChange('events')}
            />
          ) : (
            <div className="flex flex-col w-full">
              <IncidentTable
                incidents={incidentSearchResult?.incidents || []}
                loading={loadingIncidents}
                onViewDetails={handleViewIncidentDetails}
                onDelete={handleDeleteTrigger}
              />

              <Pagination
                currentPage={incidentFilters.page}
                totalPages={Math.ceil((incidentSearchResult?.total || 0) / incidentFilters.size)}
                totalItems={incidentSearchResult?.total || 0}
                itemsPerPage={incidentFilters.size}
                onPageChange={handleIncidentPageChange}
              />
            </div>
          )}
        </div>
      )}

      {/* View: Cloud Events */}
      {activeTab === 'events' && (
        <div className="flex flex-col gap-6 w-full animate-fade-in">
          <EventsToolbar
            filters={eventFilters}
            onFilterChange={setEventFilters}
            onRefresh={refetchEvents}
            isRefreshing={fetchingEvents}
          />

          {errorEvents ? (
            <div className="py-12 text-center text-red font-medium border border-border-color bg-surface/20 rounded-xl">
              Error: Failed to connect to OpenSearch events index. Please verify OpenSearch connection.
            </div>
          ) : !loadingEvents && (!eventSearchResult?.events || eventSearchResult.events.length === 0) ? (
            <EmptyEvents onRefresh={refetchEvents} />
          ) : (
            <div className="flex flex-col w-full">
              <EventsTable
                events={eventSearchResult?.events || []}
                loading={loadingEvents}
                onViewDetails={handleViewEventDetails}
              />

              <Pagination
                currentPage={eventFilters.page}
                totalPages={Math.ceil((eventSearchResult?.total || 0) / eventFilters.size)}
                totalItems={eventSearchResult?.total || 0}
                itemsPerPage={eventFilters.size}
                onPageChange={handleEventPageChange}
              />
            </div>
          )}
        </div>
      )}

      {/* Incident Detail Drawer */}
      <IncidentDrawer
        isOpen={isIncidentDrawerOpen}
        onClose={() => {
          setIsIncidentDrawerOpen(false);
          setSelectedIncidentId(null);
        }}
        incidentId={selectedIncidentId}
      />

      {/* Event Detail Inspector Drawer */}
      <EventDetailDrawer
        isOpen={isEventDrawerOpen}
        onClose={() => {
          setIsEventDrawerOpen(false);
          setSelectedEvent(null);
        }}
        event={selectedEvent}
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
