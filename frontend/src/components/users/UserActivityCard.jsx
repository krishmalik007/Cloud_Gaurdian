import React from 'react';
import { Card } from '../ui/Card';
import { HiOutlineDatabase } from 'react-icons/hi';

export default function UserActivityCard({ activity }) {
  return (
    <Card title="Recent Activity Logs" className="bg-surface/30 text-left">
      <div className="flex flex-col items-center justify-center py-6 text-center select-none text-text-muted">
        <HiOutlineDatabase className="w-8 h-8 text-text-muted opacity-30 mb-2" />
        <span className="text-[11px] font-semibold text-text-secondary">No Recent Activity Indexed</span>
        <span className="text-[10px] text-text-muted max-w-[200px] mt-0.5">
          User activities are logged directly in the system audit logs.
        </span>
      </div>
    </Card>
  );
}
