import React from 'react';
import { HiOutlineUsers } from 'react-icons/hi';
import { Button } from '../ui/Button';

export default function UsersEmptyState({ onRefresh }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center select-none bg-surface/30 border border-border-color rounded-xl w-full">
      <div className="p-4 rounded-full bg-surface border border-border-color text-text-muted opacity-50 mb-5">
        <HiOutlineUsers className="w-12 h-12 text-primary-blue" />
      </div>
      
      <h3 className="text-base font-bold text-text-primary mb-1">
        No Users Found
      </h3>
      
      <p className="text-xs text-text-secondary max-w-sm mb-6 leading-relaxed">
        Registered users will appear here after they are created.
      </p>

      <Button variant="outline" size="sm" onClick={onRefresh}>
        Refresh
      </Button>
    </div>
  );
}
