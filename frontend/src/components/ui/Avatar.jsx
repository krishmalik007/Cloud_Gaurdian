import React from 'react';

export const Avatar = ({
  username = '',
  size = 'md',
  status, // 'online' | 'offline' | 'away' | null
  className = '',
}) => {
  const getInitials = (name) => {
    if (!name) return 'CG';
    const parts = name.split(/[\s_.-]+/);
    if (parts.length > 1) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  const sizes = {
    xs: 'w-6 h-6 text-[10px]',
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm font-semibold',
    lg: 'w-12 h-12 text-base font-semibold',
    xl: 'w-16 h-16 text-lg font-bold',
  };

  const currentSize = sizes[size] || sizes.md;

  // Determine background color based on name hash for consistent color matching
  const getColorClass = (name) => {
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const colors = [
      'bg-primary-blue/20 text-primary-blue border-primary-blue/30',
      'bg-green/20 text-green border-green/30',
      'bg-orange/20 text-orange border-orange/30',
      'bg-purple/20 text-purple border-purple/30',
      'bg-red/20 text-red border-red/30',
    ];
    return colors[hash % colors.length];
  };

  const statusColors = {
    online: 'bg-green ring-background',
    offline: 'bg-text-muted ring-background',
    away: 'bg-orange ring-background',
  };

  const currentStatusColor = statusColors[status];

  return (
    <div className="relative inline-flex select-none">
      <div
        className={`flex items-center justify-center rounded-full border ${getColorClass(
          username
        )} ${currentSize} ${className}`}
      >
        {getInitials(username)}
      </div>
      {status && (
        <span
          className={`absolute bottom-0 right-0 block w-2.5 h-2.5 rounded-full ring-2 ${currentStatusColor}`}
        />
      )}
    </div>
  );
};
