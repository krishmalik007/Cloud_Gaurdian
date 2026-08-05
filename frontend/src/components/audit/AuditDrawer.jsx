import React from 'react';
import { useAuditDetail } from '../../hooks/useAudit';
import { Drawer } from '../ui/Drawer';
import { Skeleton } from '../ui/Skeleton';
import AuditUserCard from './AuditUserCard';
import AuditMetadata from './AuditMetadata';
import AuditTimeline from './AuditTimeline';
import { HiOutlineTerminal, HiOutlineDatabase, HiOutlineClock } from 'react-icons/hi';

export default function AuditDrawer({ isOpen, onClose, auditId }) {
  const { data: log, isLoading, isError } = useAuditDetail(auditId);

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={isLoading ? 'Retrieving Audit Details...' : `Audit Log: ${log?.audit_id || ''}`}
      size="lg"
    >
      {isLoading ? (
        <div className="flex flex-col gap-6 w-full animate-pulse select-none text-left">
          <Skeleton className="h-8 w-2/3" />
          <div className="grid grid-cols-2 gap-4">
            <Skeleton className="h-28" />
            <Skeleton className="h-28" />
          </div>
          <Skeleton className="h-40" />
        </div>
      ) : isError || !log ? (
        <div className="text-center py-12 text-text-muted select-none">
          Failed to fetch audit log details. Verify Admin permissions.
        </div>
      ) : (
        <div className="flex flex-col gap-6 text-left pb-10 select-none">
          {/* User Card and Meta Card Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AuditUserCard username={log.username} userId={log.user_id} />
            <AuditMetadata log={log} />
          </div>

          {/* Target Resource Pane */}
          <div className="p-4 bg-background/40 border border-border-color rounded-xl flex flex-col gap-1.5">
            <span className="text-[10px] font-bold text-text-muted uppercase">Target Resource</span>
            <span className="font-mono text-xs font-semibold text-text-primary select-all break-all mt-1">
              {log.resource}
            </span>
          </div>

          {/* Timeline Process */}
          <div className="flex flex-col gap-4 mt-2">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
              <HiOutlineClock className="w-4.5 h-4.5 text-primary-blue" />
              Ingestion Timeline
            </h4>
            <div className="pl-2 pt-2">
              <AuditTimeline timestamp={log.timestamp} />
            </div>
          </div>

          {/* Raw JSON Audit Log */}
          <div className="flex flex-col gap-3 mt-2">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
              <HiOutlineTerminal className="w-4.5 h-4.5 text-primary-blue" />
              Raw Audit Event JSON
            </h4>
            <div className="bg-background/80 border border-border-color rounded-xl p-4 font-mono text-[10px] text-green overflow-x-auto select-all max-h-60 max-w-full">
              <pre>{JSON.stringify(log, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </Drawer>
  );
}
