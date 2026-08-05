import React from 'react';
import { Card } from '../ui/Card';
import { RiGroupLine, RiAdminLine, RiUserSearchLine, RiUserUnfollowLine } from 'react-icons/ri';

export default function UsersStats({ users = [], loading = false }) {
  const total = users.length;
  const admins = users.filter((u) => String(u.role).toUpperCase() === 'ADMIN').length;
  const analysts = users.filter((u) => String(u.role).toUpperCase() === 'ANALYST').length;
  const disabled = users.filter((u) => !u.enabled).length;

  const stats = [
    { label: 'Total Personnel', value: total, icon: RiGroupLine, variant: 'info' },
    { label: 'Administrators', value: admins, icon: RiAdminLine, variant: 'danger' },
    { label: 'SOC Analysts', value: analysts, icon: RiUserSearchLine, variant: 'success' },
    { label: 'Disabled Accounts', value: disabled, icon: RiUserUnfollowLine, variant: 'warning' },
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
