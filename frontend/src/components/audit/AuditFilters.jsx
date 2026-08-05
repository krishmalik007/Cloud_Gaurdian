import React from 'react';

export default function AuditFilters({ filters, onChange }) {
  const handleSelectChange = (field, e) => {
    onChange({
      ...filters,
      [field]: e.target.value || null,
    });
  };

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Action Filter */}
      <select
        value={filters.action || ''}
        onChange={(e) => handleSelectChange('action', e)}
        className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
      >
        <option value="">All Actions</option>
        <option value="LOGIN">LOGIN</option>
        <option value="REGISTER">REGISTER</option>
        <option value="UPLOAD_LOG">UPLOAD_LOG</option>
        <option value="DELETE_INCIDENT">DELETE_INCIDENT</option>
        <option value="CREATE_IOC">CREATE_IOC</option>
        <option value="UPDATE_IOC">UPDATE_IOC</option>
        <option value="DELETE_IOC">DELETE_IOC</option>
      </select>

      {/* Status Filter */}
      <select
        value={filters.status || ''}
        onChange={(e) => handleSelectChange('status', e)}
        className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
      >
        <option value="">All Statuses</option>
        <option value="SUCCESS">SUCCESS</option>
        <option value="FAILED">FAILED</option>
      </select>

      {/* Date Range Selector */}
      <select
        value={filters.dateOrder || 'newest'}
        onChange={(e) => handleSelectChange('dateOrder', e)}
        className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
      >
        <option value="newest">Newest First</option>
        <option value="oldest">Oldest First</option>
      </select>
    </div>
  );
}
