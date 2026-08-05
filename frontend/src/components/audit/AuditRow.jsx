import React from 'react';

export default function AuditRow({ children, onClick, active = false }) {
  return (
    <tr
      onClick={onClick}
      className={`bg-transparent hover:bg-background/20 transition-colors border-b border-border-color/50 cursor-pointer ${
        active ? 'bg-primary-blue/5' : ''
      }`}
    >
      {children}
    </tr>
  );
}
