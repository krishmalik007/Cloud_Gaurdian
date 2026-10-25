import React from 'react';
import { HiOutlineRefresh, HiOutlineSearch, HiOutlineX } from 'react-icons/hi';
import { Button } from '../ui/Button';

export default function EventsToolbar({ filters, onFilterChange, onRefresh, isRefreshing = false }) {
  const handleSearchChange = (e) => {
    onFilterChange({
      ...filters,
      search: e.target.value || null,
      page: 1,
    });
  };

  const clearSearch = () => {
    onFilterChange({
      ...filters,
      search: null,
      page: 1,
    });
  };

  const handleProviderChange = (e) => {
    onFilterChange({
      ...filters,
      provider: e.target.value || null,
      page: 1,
    });
  };

  const handleRiskChange = (e) => {
    onFilterChange({
      ...filters,
      risk_level: e.target.value || null,
      page: 1,
    });
  };

  const handleStatusChange = (e) => {
    onFilterChange({
      ...filters,
      status: e.target.value || null,
      page: 1,
    });
  };

  const handleRegionChange = (e) => {
    onFilterChange({
      ...filters,
      region: e.target.value || null,
      page: 1,
    });
  };

  const handleTypeChange = (e) => {
    const val = e.target.value;
    onFilterChange({
      ...filters,
      is_incident: val === 'true' ? true : val === 'false' ? false : null,
      page: 1,
    });
  };

  const handleClearAllFilters = () => {
    onFilterChange({
      ...filters,
      provider: null,
      risk_level: null,
      status: null,
      username: null,
      event_name: null,
      event_type: null,
      region: null,
      search: null,
      is_incident: null,
      page: 1,
    });
  };

  const isFiltered = Boolean(
    filters.search ||
    filters.provider ||
    filters.risk_level ||
    filters.status ||
    filters.region ||
    filters.is_incident !== null
  );

  return (
    <div className="flex flex-col gap-4 p-4 border border-border-color bg-surface/50 rounded-xl w-full">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 w-full">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[260px]">
          <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Search by event name, user, IP, or ID (e.g. ConsoleLogin)..."
            value={filters.search || ''}
            onChange={handleSearchChange}
            className="w-full pl-9 pr-9 py-2 text-xs bg-background border border-border-color rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:border-primary-blue transition-colors"
          />
          {filters.search && (
            <button
              onClick={clearSearch}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary p-0.5 rounded cursor-pointer"
              title="Clear search query"
            >
              <HiOutlineX className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Filter Dropdowns and Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Provider */}
          <select
            value={filters.provider || ''}
            onChange={handleProviderChange}
            className="px-2.5 py-2 text-xs bg-background border border-border-color rounded-lg text-text-secondary focus:outline-none focus:border-primary-blue"
          >
            <option value="">All Providers</option>
            <option value="AWS">AWS</option>
            <option value="AZURE">Azure</option>
            <option value="GCP">GCP</option>
          </select>

          {/* Severity / Risk Level */}
          <select
            value={filters.risk_level || ''}
            onChange={handleRiskChange}
            className="px-2.5 py-2 text-xs bg-background border border-border-color rounded-lg text-text-secondary focus:outline-none focus:border-primary-blue"
          >
            <option value="">All Severities</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>

          {/* Status */}
          <select
            value={filters.status || ''}
            onChange={handleStatusChange}
            className="px-2.5 py-2 text-xs bg-background border border-border-color rounded-lg text-text-secondary focus:outline-none focus:border-primary-blue"
          >
            <option value="">All Statuses</option>
            <option value="INFORMATIONAL">Informational</option>
            <option value="OPERATIONAL_HEALTH">Operational Health</option>
            <option value="OPEN">Open Alert</option>
            <option value="RESOLVED">Resolved</option>
          </select>

          {/* Region */}
          <select
            value={filters.region || ''}
            onChange={handleRegionChange}
            className="px-2.5 py-2 text-xs bg-background border border-border-color rounded-lg text-text-secondary focus:outline-none focus:border-primary-blue"
          >
            <option value="">All Regions</option>
            <option value="ap-south-1">ap-south-1 (Mumbai)</option>
            <option value="eu-north-1">eu-north-1 (Stockholm)</option>
            <option value="us-east-1">us-east-1 (N. Virginia)</option>
            <option value="us-west-2">us-west-2 (Oregon)</option>
            <option value="us-east-2">us-east-2 (Ohio)</option>
            <option value="Unknown">Unknown Region</option>
          </select>

          {/* Classification */}
          <select
            value={filters.is_incident === true ? 'true' : filters.is_incident === false ? 'false' : ''}
            onChange={handleTypeChange}
            className="px-2.5 py-2 text-xs bg-background border border-border-color rounded-lg text-text-secondary focus:outline-none focus:border-primary-blue"
          >
            <option value="">All Events</option>
            <option value="false">Routine / Informational</option>
            <option value="true">Security Incidents Only</option>
          </select>

          {/* Clear Filters Button */}
          {isFiltered && (
            <button
              onClick={handleClearAllFilters}
              className="px-3 py-2 text-xs bg-surface hover:bg-background border border-border-color rounded-lg text-text-secondary hover:text-text-primary transition-colors flex items-center gap-1 cursor-pointer"
              title="Reset all search and filter options"
            >
              <HiOutlineX className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          )}

          {/* Refresh */}
          <Button
            variant="outline"
            size="sm"
            onClick={onRefresh}
            isLoading={isRefreshing}
            className="!p-2.5 h-[34px] w-[34px]"
            title="Refresh Events (Preserves Active Filters)"
          >
            {!isRefreshing && <HiOutlineRefresh className="w-4 h-4" />}
          </Button>
        </div>
      </div>
    </div>
  );
}
