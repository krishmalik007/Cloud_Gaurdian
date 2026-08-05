import React from 'react';
import { HiOutlineFilter } from 'react-icons/hi';

export default function IncidentFilters({ filters, onChange }) {
  const handleSelectChange = (field, e) => {
    onChange({
      ...filters,
      [field]: e.target.value || null,
      page: 1, // reset page on filter change
    });
  };

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Provider Filter */}
      <div className="flex flex-col gap-1 text-left">
        <select
          value={filters.provider || ''}
          onChange={(e) => handleSelectChange('provider', e)}
          className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
        >
          <option value="">All Providers</option>
          <option value="AWS">AWS</option>
          <option value="Azure">Azure</option>
          <option value="GCP">GCP</option>
        </select>
      </div>

      {/* Severity Filter */}
      <div className="flex flex-col gap-1 text-left">
        <select
          value={filters.risk_level || ''}
          onChange={(e) => handleSelectChange('risk_level', e)}
          className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      {/* Status Filter */}
      <div className="flex flex-col gap-1 text-left">
        <select
          value={filters.status || ''}
          onChange={(e) => handleSelectChange('status', e)}
          className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
        >
          <option value="">All Statuses</option>
          <option value="OPEN">Open</option>
          <option value="INVESTIGATING">Investigating</option>
          <option value="RESOLVED">Resolved</option>
          <option value="CLOSED">Closed</option>
        </select>
      </div>

      {/* Sort By Filter */}
      <div className="flex flex-col gap-1 text-left">
        <select
          value={filters.sort_by || 'created_at'}
          onChange={(e) => handleSelectChange('sort_by', e)}
          className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
        >
          <option value="created_at">Created Time</option>
          <option value="risk_score">Risk Score</option>
        </select>
      </div>

      {/* Sort Order */}
      <div className="flex flex-col gap-1 text-left">
        <select
          value={filters.sort_order || 'desc'}
          onChange={(e) => handleSelectChange('sort_order', e)}
          className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
      </div>
    </div>
  );
}
