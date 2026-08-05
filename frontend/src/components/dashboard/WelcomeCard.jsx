import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Avatar } from '../ui/Avatar';
import { Badge } from '../ui/Badge';

export default function WelcomeCard() {
  const { user } = useAuth();
  const [greeting, setGreeting] = useState('Welcome');

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) {
      setGreeting('Good Morning');
    } else if (hour < 18) {
      setGreeting('Good Afternoon');
    } else {
      setGreeting('Good Evening');
    }
  }, []);

  return (
    <div className="bg-surface border border-border-color rounded-xl p-6 flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm">
      <div className="flex items-center gap-4 text-left">
        <Avatar username={user?.username || 'Analyst'} size="lg" status="online" className="ring-2 ring-primary-blue/30" />
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className="text-xs text-text-muted font-bold uppercase tracking-wider">Security Operations Center</span>
            <Badge variant={user?.role === 'ADMIN' ? 'purple' : 'info'} size="sm">
              {user?.role || 'ANALYST'}
            </Badge>
          </div>
          <h2 className="text-xl font-bold text-text-primary tracking-tight">
            {greeting}, {user?.username || 'SecOps Analyst'}
          </h2>
          <p className="text-xs text-text-secondary">
            Operational dashboard is monitoring active log streams for indicators of compromise.
          </p>
        </div>
      </div>
      
      <div className="text-right hidden md:block">
        <div className="text-[10px] font-bold text-text-muted uppercase tracking-wider select-none">Current Time</div>
        <div className="text-sm font-semibold text-text-primary">
          {new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}
        </div>
        <div className="text-xs text-text-secondary mt-0.5">
          {new Date().toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}
