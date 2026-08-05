import React from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { RiAlertLine, RiGlobeLine, RiUserLine, RiPlayLine, RiShieldLine } from 'react-icons/ri';

export default function IOCStats({ iocs = [], loading = false }) {
  const total = iocs.length;
  const active = iocs.filter((i) => i.enabled).length;
  const ips = iocs.filter((i) => String(i.type).toUpperCase() === 'IP').length;
  const domains = iocs.filter((i) => String(i.type).toUpperCase() === 'DOMAIN').length;
  const users = iocs.filter((i) => String(i.type).toUpperCase() === 'USERNAME').length;

  const stats = [
    { label: 'Total Indicators', value: total, icon: RiShieldLine, variant: 'info' },
    { label: 'Active Watchlist', value: active, icon: RiPlayLine, variant: 'success' },
    { label: 'Network IPs', value: ips, icon: RiAlertLine, variant: 'warning' },
    { label: 'Active Domains', value: domains, icon: RiGlobeLine, variant: 'purple' },
    { label: 'Suspicious Users', value: users, icon: RiUserLine, variant: 'info' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 select-none">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <Card key={idx} title={stat.label} className="!p-4 bg-surface/30">
            <div className="flex items-center justify-between mt-2">
              <span className="text-xl font-extrabold text-text-primary">
                {loading ? '...' : stat.value}
              </span>
              <div className="text-text-muted opacity-40">
                <Icon className="w-5 h-5" />
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
