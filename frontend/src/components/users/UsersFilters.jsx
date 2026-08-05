import React from 'react';

export default function UsersFilters({ filters, onChange }) {
  const handleSelectChange = (field, e) => {
    onChange({
      ...filters,
      [field]: e.target.value || null,
    });
  };

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Role Filter */}
      <select
        value={filters.role || ''}
        onChange={(e) => handleSelectChange('role', e)}
        className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
      >
        <option value="">All Roles</option>
        <option value="ADMIN">ADMIN</option>
        <option value="ANALYST">ANALYST</option>
      </select>

      {/* Status Filter */}
      <select
        value={filters.enabled === null ? '' : String(filters.enabled)}
        onChange={(e) => {
          const val = e.target.value;
          onChange({
            ...filters,
            enabled: val === 'true' ? true : val === 'false' ? false : null,
          });
        }}
        className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
      >
        <option value="">All Statuses</option>
        <option value="true">Active</option>
        <option value="false">Disabled</option>
      </select>

      {/* Order Filter */}
      <select
        value={filters.order || 'newest'}
        onChange={(e) => handleSelectChange('order', e)}
        className="bg-surface border border-border-color rounded-lg px-3 py-1.5 text-xs text-text-primary outline-none focus:border-primary-blue"
      >
        <option value="newest">Newest First</option>
        <option value="oldest">Oldest First</option>
      </select>
    </div>
  );
}
