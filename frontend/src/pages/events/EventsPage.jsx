import React, { useState } from 'react';
import { useEventsSearch, useEventStats } from '../../hooks/useEvents';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Pagination } from '../../components/ui/Pagination';
import EventsToolbar from '../../components/events/EventsToolbar';
import EventsTable from '../../components/events/EventsTable';
import EventDetailDrawer from '../../components/events/EventDetailDrawer';
import EmptyEvents from '../../components/events/EmptyEvents';

export default function EventsPage() {
  const [filters, setFilters] = useState({
    provider: null,
    risk_level: null,
    status: null,
    region: null,
    event_type: null,
    username: null,
    search: null,
    is_incident: null,
    page: 1,
    size: 15,
    sort_by: 'timestamp',
    sort_order: 'desc',
  });

  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const { data: searchResult, isLoading, isFetching, refetch, isError } = useEventsSearch(filters);
  const { data: statsData, isLoading: loadingStats } = useEventStats();

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({
      ...prev,
      page: newPage,
    }));
  };

  const handleViewDetails = (event) => {
    setSelectedEvent(event);
    setIsDrawerOpen(true);
  };

  const totalEvents = statsData?.total_events || searchResult?.total || 0;
  const informationalEvents = statsData?.informational_events || 0;
  const incidentEvents = statsData?.incident_events || 0;
  const awsEvents = statsData?.providers?.find((p) => p.provider === 'AWS')?.count || 0;

  return (
    <div className="flex flex-col gap-6 w-full animate-fade-in text-left">
      <PageHeader
        title="Cloud Audit Log & Telemetry Events"
        subtitle="Search, filter, and inspect all ingested CloudTrail, Azure, and GCP activity records in real time."
      />

      {/* Stats Summary Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 select-none">
        <Card title="Total Telemetry" subtitle="All ingested events" className="!p-4 bg-surface/30 border-l-2 border-l-primary-blue">
          <span className="text-xl font-extrabold text-text-primary block mt-1">
            {loadingStats ? '...' : totalEvents.toLocaleString()}
          </span>
        </Card>
        <Card title="AWS CloudTrail" subtitle="S3 & SQS logs" className="!p-4 bg-surface/30 border-l-2 border-l-orange">
          <span className="text-xl font-extrabold text-orange block mt-1">
            {loadingStats ? '...' : awsEvents.toLocaleString()}
          </span>
        </Card>
        <Card title="Informational" subtitle="Routine cloud activity" className="!p-4 bg-surface/30 border-l-2 border-l-green">
          <span className="text-xl font-extrabold text-green block mt-1">
            {loadingStats ? '...' : informationalEvents.toLocaleString()}
          </span>
        </Card>
        <Card title="Security Alerts" subtitle="Correlated incidents" className="!p-4 bg-surface/30 border-l-2 border-l-red">
          <span className="text-xl font-extrabold text-red block mt-1">
            {loadingStats ? '...' : incidentEvents.toLocaleString()}
          </span>
        </Card>
      </div>

      {/* Events Toolbar */}
      <EventsToolbar
        filters={filters}
        onFilterChange={setFilters}
        onRefresh={refetch}
        isRefreshing={isFetching}
      />

      {/* Events Table */}
      {isError ? (
        <div className="py-12 text-center text-red font-medium border border-border-color bg-surface/20 rounded-xl">
          Error: Failed to connect to OpenSearch events index. Please verify OpenSearch connection.
        </div>
      ) : !isLoading && (!searchResult?.events || searchResult.events.length === 0) ? (
        <EmptyEvents onRefresh={refetch} />
      ) : (
        <div className="flex flex-col w-full">
          <EventsTable
            events={searchResult?.events || []}
            loading={isLoading}
            onViewDetails={handleViewDetails}
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
      <EventDetailDrawer
        isOpen={isDrawerOpen}
        onClose={() => {
          setIsDrawerOpen(false);
          setSelectedEvent(null);
        }}
        event={selectedEvent}
      />
    </div>
  );
}
