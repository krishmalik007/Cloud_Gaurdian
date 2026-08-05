import React from 'react';
import { HiOutlineRefresh } from 'react-icons/hi';
import AuditSearch from './AuditSearch';
import AuditFilters from './AuditFilters';
import { Button } from '../ui/Button';

export default function AuditToolbar({ search, onSearchChange, filters, onFilterChange, onRefresh, isRefreshing = false }) {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 border border-border-color bg-surface/50 rounded-xl w-full">
      {/* Search Bar */}
      <AuditSearch value={search} onChange={onSearchChange} />

      {/* Filters & Actions */}
      <div className="flex flex-wrap items-center gap-3">
        <AuditFilters filters={filters} onChange={onFilterChange} />
        
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
