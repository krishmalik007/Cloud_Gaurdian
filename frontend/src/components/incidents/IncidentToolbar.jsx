import React from 'react';
import { HiOutlineRefresh } from 'react-icons/hi';
import IncidentSearch from './IncidentSearch';
import IncidentFilters from './IncidentFilters';
import { Button } from '../ui/Button';

export default function IncidentToolbar({ filters, onFilterChange, onRefresh, isRefreshing = false }) {
  const handleSearchChange = (searchTerm) => {
    onFilterChange({
      ...filters,
      username: searchTerm || null, // we can map text search to username or other fields
      page: 1, // reset page
    });
  };

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 border border-border-color bg-surface/50 rounded-xl w-full">
      {/* Search Bar */}
      <IncidentSearch value={filters.username || ''} onChange={handleSearchChange} />

      {/* Filters & Refresh Button */}
      <div className="flex flex-wrap items-center gap-3">
        <IncidentFilters filters={filters} onChange={onFilterChange} />
        
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          isLoading={isRefreshing}
          className="!p-2.5 h-[34px] w-[34px]"
        >
          {!isRefreshing && <HiOutlineRefresh className="w-4 h-4" />}
        </Button>
      </div>
    </div>
  );
}
