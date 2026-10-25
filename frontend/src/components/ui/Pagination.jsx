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
          {(() => {
            const pages = [];
            if (totalPages <= 7) {
              for (let i = 1; i <= totalPages; i++) pages.push(i);
            } else if (currentPage <= 4) {
              pages.push(1, 2, 3, 4, 5, '...', totalPages);
            } else if (currentPage >= totalPages - 3) {
              pages.push(1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
            } else {
              pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
            }

            return pages.map((item, idx) => {
              if (item === '...') {
                return (
                  <span key={`ellipsis-${idx}`} className="text-text-muted px-1.5 text-xs select-none">
                    ...
                  </span>
                );
              }
              return (
                <Button
                  key={item}
                  variant={item === currentPage ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => onPageChange(item)}
                  className={`w-8 h-8 !p-0 ${item === currentPage ? 'shadow-none' : ''}`}
                >
                  {item}
                </Button>
              );
            });
          })()}
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
