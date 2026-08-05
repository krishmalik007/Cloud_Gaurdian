import React from 'react';
import { Skeleton } from './Skeleton';

export const Table = ({
  columns = [],
  data = [],
  isLoading = false,
  onRowClick,
  emptyMessage = 'No data available',
  emptySubMessage = 'Try adjusting your filters or upload logs to get started.',
  emptyAction,
  renderRow,
}) => {
  return (
    <div className="w-full bg-surface border border-border-color rounded-xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto w-full">
        <table className="w-full border-collapse text-left text-sm text-text-secondary">
          <thead className="bg-sidebar/50 border-b border-border-color sticky top-0 text-xs font-semibold text-text-muted select-none uppercase tracking-wider">
            <tr>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className={`px-6 py-4 font-semibold ${col.className || ''}`}
                  style={{ width: col.width || 'auto' }}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-color/50">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, rIdx) => (
                <tr key={rIdx} className="bg-transparent">
                  {columns.map((col, cIdx) => (
                    <td key={cIdx} className="px-6 py-4">
                      <Skeleton className="h-4 w-full rounded" />
                    </td>
                  ))}
                </tr>
              ))
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-12 text-center">
                  <div className="flex flex-col items-center justify-center gap-3">
                    <svg className="w-12 h-12 text-text-muted opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                    </svg>
                    <div className="flex flex-col gap-0.5">
                      <p className="text-sm font-semibold text-text-primary">
                        {emptyMessage}
                      </p>
                      <p className="text-xs text-text-muted">
                        {emptySubMessage}
                      </p>
                    </div>
                    {emptyAction && <div className="mt-2">{emptyAction}</div>}
                  </div>
                </td>
              </tr>
            ) : (
              data.map((item, idx) => {
                if (renderRow) {
                  return renderRow(item, idx, onRowClick);
                }
                return (
                  <tr
                    key={idx}
                    onClick={onRowClick ? () => onRowClick(item) : undefined}
                    className={`bg-transparent hover:bg-background/20 transition-colors border-b border-border-color/50 ${
                      onRowClick ? 'cursor-pointer' : ''
                    }`}
                  >
                    {columns.map((col, cIdx) => {
                      const value = item[col.accessor];
                      return (
                        <td key={cIdx} className="px-6 py-4 font-normal text-text-secondary">
                          {col.render ? col.render(item) : value !== undefined ? String(value) : '-'}
                        </td>
                      );
                    })}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
