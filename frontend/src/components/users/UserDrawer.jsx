import React from 'react';
import { useUserDetail } from '../../hooks/useUsers';
import { Drawer } from '../ui/Drawer';
import { Skeleton } from '../ui/Skeleton';
import UserProfileCard from './UserProfileCard';
import UserActivityCard from './UserActivityCard';
import { HiOutlineTerminal } from 'react-icons/hi';

export default function UserDrawer({ isOpen, onClose, userId }) {
  const { data: user, isLoading, isError } = useUserDetail(userId);

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={isLoading ? 'Loading User Profile...' : `User: ${user?.username || ''}`}
      size="lg"
    >
      {isLoading ? (
        <div className="flex flex-col gap-6 w-full animate-pulse select-none text-left">
          <Skeleton className="h-8 w-2/3" />
          <Skeleton className="h-40" />
          <Skeleton className="h-28" />
        </div>
      ) : isError || !user ? (
        <div className="text-center py-12 text-text-muted select-none">
          Failed to fetch user details. Verify Admin permissions.
        </div>
      ) : (
        <div className="flex flex-col gap-6 text-left pb-10 select-none">
          {/* User Profile Properties */}
          <UserProfileCard user={user} />

          {/* User Activity log placeholder */}
          <UserActivityCard activity={user.recent_activity} />

          {/* Raw JSON View */}
          <div className="flex flex-col gap-3 mt-2">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
              <HiOutlineTerminal className="w-4.5 h-4.5 text-primary-blue" />
              Raw User JSON Record
            </h4>
            <div className="bg-background/80 border border-border-color rounded-xl p-4 font-mono text-[10px] text-green overflow-x-auto select-all max-h-60 max-w-full">
              <pre>{JSON.stringify(user, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </Drawer>
  );
}
