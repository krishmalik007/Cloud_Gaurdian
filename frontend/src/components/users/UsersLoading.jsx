import React from 'react';
import { Skeleton } from '../ui/Skeleton';

export default function UsersLoading() {
  return (
    <div className="flex flex-col gap-6 w-full animate-pulse select-none">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
      <Skeleton className="h-64 w-full" />
    </div>
  );
}
