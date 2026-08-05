import React from 'react';
import { HiOutlineChevronLeft, HiOutlineChevronRight } from 'react-icons/hi';
import { Button } from './Button';

export const Pagination = ({
  currentPage = 1,
  totalPages = 1,
  totalItems = 0,
  itemsPerPage = 10,
  onPageChange,
  className = '',
}) => {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  if (totalPages <= 1) return null;

  return (
    <div className={`flex flex-col sm:flex-row items-center justify-between gap-4 px-6 py-4 border-t border-border-color bg-surface w-full rounded-b-xl select-none ${className}`}>
      <div className="text-xs text-text-muted">
        Showing <span className="font-semibold text-text-secondary">{totalItems > 0 ? startItem : 0}</span> to{' '}
        <span className="font-semibold text-text-secondary">{endItem}</span> of{' '}
        <span className="font-semibold text-text-secondary">{totalItems}</span> results
      </div>
      
      <div className="flex items-center gap-1.5">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          <HiOutlineChevronLeft className="w-4 h-4 mr-1" />
          Previous
        </Button>
        
        <div className="flex items-center gap-1">
          {Array.from({ length: totalPages }).map((_, idx) => {
            const pageNum = idx + 1;
            // Show first page, last page, current page, and pages immediately adjacent to current page
            if (
              pageNum === 1 ||
              pageNum === totalPages ||
              Math.abs(pageNum - currentPage) <= 1
            ) {
              return (
                <Button
                  key={pageNum}
                  variant={pageNum === currentPage ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => onPageChange(pageNum)}
                  className={`w-8 h-8 !p-0 ${
                    pageNum === currentPage ? 'shadow-none' : ''
                  }`}
                >
                  {pageNum}
                </Button>
              );
            } else if (
              pageNum === 2 ||
              pageNum === totalPages - 1
            ) {
              return (
                <span key={pageNum} className="text-text-muted px-1 text-xs select-none">
                  ...
                </span>
              );
            }
            return null;
          })}
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
          <HiOutlineChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
    </div>
  );
};
