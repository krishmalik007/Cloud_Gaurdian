import React from 'react';
import { HiOutlineUser, HiOutlineTag } from 'react-icons/hi';

export default function AuditUserCard({ username, userId }) {
  // Infer role safely or display unmapped status
  const getRole = (name) => {
    if (name === 'admin' || name === 'krish') return 'Administrator';
    return 'Security Analyst';
  };

  return (
    <div className="flex flex-col gap-3 p-4 border border-border-color rounded-xl bg-surface/20 text-left select-none">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-primary-blue/15 text-primary-blue rounded-lg">
          <HiOutlineUser className="w-5 h-5" />
        </div>
        <div className="flex flex-col gap-0.5">
          <span className="text-xs font-bold text-text-primary truncate max-w-[150px]">{username}</span>
          <span className="text-[10px] text-text-muted">{getRole(username)}</span>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs border-t border-border-color/30 pt-2 mt-1">
        <span className="text-text-muted flex items-center gap-1.5">
          <HiOutlineTag className="w-4 h-4" />
          User ID
        </span>
        <span className="font-mono text-[10px] text-text-secondary select-all">{userId || '-'}</span>
      </div>
    </div>
  );
}
