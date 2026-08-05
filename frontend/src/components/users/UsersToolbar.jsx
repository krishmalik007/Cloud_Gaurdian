import React from 'react';
import { HiOutlineRefresh } from 'react-icons/hi';
import UsersSearch from './UsersSearch';
import UsersFilters from './UsersFilters';
import { Button } from '../ui/Button';

export default function UsersToolbar({ search, onSearchChange, filters, onFilterChange, onRefresh, isRefreshing = false }) {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 border border-border-color bg-surface/50 rounded-xl w-full">
      {/* Search Field */}
      <UsersSearch value={search} onChange={onSearchChange} />

      {/* Filters & Actions */}
      <div className="flex flex-wrap items-center gap-3">
        <UsersFilters filters={filters} onChange={onFilterChange} />
        
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
