import React from 'react';
import AuditActionBadge from './AuditActionBadge';
import AuditStatusBadge from './AuditStatusBadge';
import { HiOutlineTag, HiOutlineShieldCheck, HiOutlineGlobe, HiOutlineClock } from 'react-icons/hi';

export default function AuditMetadata({ log }) {
  return (
    <div className="flex flex-col gap-3.5 p-4 border border-border-color rounded-xl bg-surface/20 text-left select-none">
      <div className="flex items-center justify-between text-xs">
        <span className="text-text-muted flex items-center gap-1.5">
          <HiOutlineTag className="w-4 h-4" />
          Event Action
        </span>
        <AuditActionBadge action={log.action} size="sm" />
      </div>

      <div className="flex items-center justify-between text-xs">
        <span className="text-text-muted flex items-center gap-1.5">
          <HiOutlineShieldCheck className="w-4 h-4" />
          Status
        </span>
        <AuditStatusBadge status={log.status} size="sm" />
      </div>

      <div className="flex items-center justify-between text-xs">
        <span className="text-text-muted flex items-center gap-1.5">
          <HiOutlineGlobe className="w-4 h-4" />
          IP Address
        </span>
        <span className="font-mono text-[10px] text-text-primary">{log.ip_address || '-'}</span>
      </div>

      <div className="flex items-center justify-between text-xs">
        <span className="text-text-muted flex items-center gap-1.5">
          <HiOutlineClock className="w-4 h-4" />
          Logged Time
        </span>
        <span className="font-semibold text-text-secondary text-[10px]">
          {new Date(log.timestamp).toLocaleString()}
        </span>
      </div>
    </div>
  );
}
