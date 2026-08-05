import React from 'react';
import { Card } from '../ui/Card';
import { RiShieldLine, RiCheckDoubleLine, RiAlertLine, RiUserSharedLine } from 'react-icons/ri';

export default function AuditStats({ logs = [], loading = false }) {
  const total = logs.length;
  const success = logs.filter((l) => String(l.status).toUpperCase() === 'SUCCESS').length;
  const failed = logs.filter((l) => String(l.status).toUpperCase() === 'FAILED').length;
  
  // Unique users
  const uniqueUsers = new Set(logs.map((l) => l.username)).size;

  const stats = [
    { label: 'Total Logs', value: total, icon: RiShieldLine, variant: 'info' },
    { label: 'Successful Tasks', value: success, icon: RiCheckDoubleLine, variant: 'success' },
    { label: 'Failed Checks', value: failed, icon: RiAlertLine, variant: 'danger' },
    { label: 'Active Personnel', value: uniqueUsers, icon: RiUserSharedLine, variant: 'info' },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 select-none">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <Card key={idx} title={stat.label} className="!p-4 bg-surface/30">
            <div className="flex items-center justify-between mt-2">
              <span className="text-xl font-extrabold text-text-primary">
                {loading ? '...' : stat.value}
              </span>
              <div className="text-text-muted opacity-30">
                <Icon className="w-5 h-5" />
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
