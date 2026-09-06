import React from 'react';
import useAuth from '../../hooks/useAuth';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Avatar } from '../../components/ui/Avatar';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { HiOutlineUser, HiOutlineMail, HiOutlineShieldCheck, HiOutlineKey } from 'react-icons/hi';

export default function Profile() {
  const { user } = useAuth();

  return (
    <div className="flex flex-col gap-6 text-left select-none">
      <PageHeader
        title="Security Analyst Profile"
        subtitle="Manage your platform credentials, API tokens, and operational roles."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <Card className="lg:col-span-1 bg-surface/30">
          <div className="flex flex-col items-center text-center p-4">
            <Avatar username={user?.username} size="lg" className="w-20 h-20 text-xl mb-4" />
            <h3 className="text-base font-bold text-text-primary">{user?.username || 'Analyst'}</h3>
            <span className="text-[10px] uppercase font-bold text-text-muted mt-0.5 tracking-wider">
              {user?.role || 'ANALYST'} Role
            </span>
            <div className="mt-4 flex flex-wrap gap-2 justify-center">
              <Badge variant={user?.role === 'ADMIN' ? 'danger' : 'info'} size="sm">
                {user?.role === 'ADMIN' ? 'Full Control' : 'Security Analyst'}
              </Badge>
              <Badge variant="success" size="sm">
                Active Session
              </Badge>
            </div>
          </div>

          <div className="border-t border-border-color/30 mt-6 pt-5 flex flex-col gap-3.5 px-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-text-muted flex items-center gap-1.5">
                <HiOutlineUser className="w-4 h-4 text-primary-blue" />
                Username
              </span>
              <span className="font-semibold text-text-primary">{user?.username}</span>
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-text-muted flex items-center gap-1.5">
                <HiOutlineMail className="w-4 h-4 text-primary-blue" />
                Email
              </span>
              <span className="font-semibold text-text-primary">{user?.email || 'N/A'}</span>
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-text-muted flex items-center gap-1.5">
                <HiOutlineShieldCheck className="w-4 h-4 text-primary-blue" />
                Security Access
              </span>
              <span className="font-semibold text-text-primary capitalize">{user?.role?.toLowerCase() || 'analyst'} privileges</span>
            </div>
          </div>
        </Card>

        {/* Analyst Information */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card title="Analyst Information" subtitle="Operational roles and system privileges" className="bg-surface/30">
            <div className="flex flex-col gap-5 pt-2">
              <div className="p-5 bg-background/50 border border-border-color rounded-xl flex flex-col gap-4">
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[10px] text-text-muted uppercase tracking-wider font-bold">Role</span>
                    <span className="text-sm font-bold text-text-primary capitalize">{user?.role?.toLowerCase() || 'Security Analyst'}</span>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[10px] text-text-muted uppercase tracking-wider font-bold">Access Level</span>
                    <span className="text-sm font-bold text-text-primary">{user?.role === 'ADMIN' ? 'Administrator Privileges' : 'Analyst Privileges'}</span>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[10px] text-text-muted uppercase tracking-wider font-bold">Session Status</span>
                    <Badge variant="success" size="sm" className="w-max">Active</Badge>
                  </div>
                </div>

                <div className="mt-2 border-t border-border-color/30 pt-4">
                  <h4 className="text-[10px] font-bold text-text-muted uppercase tracking-wider mb-3">
                    Responsibilities
                  </h4>
                  <ul className="list-disc pl-4 text-xs text-text-secondary flex flex-col gap-2">
                    <li>Monitor and investigate security incidents</li>
                    <li>Review correlated cloud activity</li>
                    <li>Analyze risk and threat scores</li>
                    <li>Review investigation notes and incident timelines</li>
                    {user?.role === 'ADMIN' && (
                      <li className="text-red font-semibold pt-1">Administrator access: Can modify all system watchlists, users, and read audit trails</li>
                    )}
                  </ul>
                </div>

              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
