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

        {/* Security Credentials & API keys */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card title="Security Credentials" subtitle="Access tokens and configuration" className="bg-surface/30">
            <div className="flex flex-col gap-5 pt-2">
              <div className="p-4 bg-background/50 border border-border-color rounded-xl flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-text-primary flex items-center gap-2">
                    <HiOutlineKey className="w-4 h-4 text-yellow" />
                    Web API Access Key
                  </span>
                  <Badge variant="info" size="xs">Active</Badge>
                </div>
                <p className="text-[11px] text-text-secondary leading-relaxed">
                  Authentication token used to invoke the CloudGuardian FastAPI router endpoints.
                </p>
                <div className="bg-surface border border-border-color rounded p-2.5 font-mono text-[9px] text-text-muted select-all overflow-x-auto">
                  {localStorage.getItem('cg_access_token') || 'Token not loaded in storage'}
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider">
                  Analyst Privileges
                </h4>
                <ul className="list-disc pl-4 text-xs text-text-secondary flex flex-col gap-1.5 mt-1">
                  <li>Can run real-time OSINT indicators against open databases</li>
                  <li>Can submit cloud audit log files to trigger automated correlation pipelines</li>
                  <li>Can view security incidents and associated logs timeline</li>
                  {user?.role === 'ADMIN' && (
                    <li className="text-red font-semibold">Administrator access: Can modify all system watchlists, users, and read audit trails</li>
                  )}
                </ul>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
