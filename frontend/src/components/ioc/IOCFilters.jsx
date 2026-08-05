import React from 'react';
import { HiOutlineSearch } from 'react-icons/hi';
import { Input } from '../ui/Input';

export default function IOCFilters({ search, onSearchChange, filters, onFilterChange }) {
  const handleSelectChange = (field, e) => {
    onFilterChange({
      ...filters,
      [field]: e.target.value || null,
    });
  };

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 border border-border-color bg-surface/50 rounded-xl w-full">
      {/* Search Input */}
      <div className="w-full md:max-w-xs">
        <Input
          placeholder="Filter indicator patterns..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          icon={HiOutlineSearch}
          containerClassName="!gap-0"
          className="!py-1.5"
        />
      </div>

      {/* Select Filters */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Type Filter */}
        <select
          value={filters.type || ''}
          onChange={(e) => handleSelectChange('type', e)}
          className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
        >
          <option value="">All Types</option>
          <option value="IP">IP Address</option>
          <option value="DOMAIN">Domain Name</option>
          <option value="USERNAME">Username</option>
        </select>

        {/* Severity Filter */}
        <select
          value={filters.severity || ''}
          onChange={(e) => handleSelectChange('severity', e)}
          className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>

        {/* Status Filter */}
        <select
          value={filters.enabled === null ? '' : String(filters.enabled)}
          onChange={(e) => {
            const val = e.target.value;
            onFilterChange({
              ...filters,
              enabled: val === 'true' ? true : val === 'false' ? false : null,
            });
          }}
          className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
        >
          <option value="">All Statuses</option>
          <option value="true">Active Watchlist</option>
          <option value="false">Disabled</option>
        </select>
      </div>
    </div>
  );
}
