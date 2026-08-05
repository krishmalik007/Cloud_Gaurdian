import React from 'react';
import { Avatar } from '../ui/Avatar';
import UserRoleBadge from './UserRoleBadge';
import UserStatusBadge from './UserStatusBadge';
import { HiOutlineMail, HiOutlineIdentification, HiOutlineCalendar } from 'react-icons/hi';

export default function UserProfileCard({ user }) {
  if (!user) return null;

  return (
    <div className="flex flex-col gap-4 p-5 border border-border-color rounded-xl bg-surface/20 text-left select-none">
      <div className="flex items-center gap-4">
        <Avatar name={user.username} size="lg" />
        <div className="flex flex-col gap-0.5">
          <span className="text-sm font-bold text-text-primary">{user.username}</span>
          <span className="text-[10px] text-text-muted">User Profile Account</span>
        </div>
      </div>

      <div className="flex flex-col gap-3.5 border-t border-border-color/30 pt-3.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-text-muted flex items-center gap-1.5">
            <HiOutlineIdentification className="w-4 h-4" />
            User ID
          </span>
          <span className="font-mono text-[10px] text-text-primary select-all">{user.user_id}</span>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-text-muted flex items-center gap-1.5">
            <HiOutlineMail className="w-4 h-4" />
            Email Address
          </span>
          <span className="font-semibold text-text-primary select-all">{user.email || '-'}</span>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-text-muted font-medium">Authorization Role</span>
          <UserRoleBadge role={user.role} size="sm" />
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-text-muted font-medium">Status</span>
          <UserStatusBadge enabled={user.enabled} size="sm" />
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-text-muted flex items-center gap-1.5">
            <HiOutlineCalendar className="w-4 h-4" />
            Created At
          </span>
          <span className="font-semibold text-text-secondary text-[10px]">
            {new Date(user.created_at).toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
}
