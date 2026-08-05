import React from 'react';
import { HiOutlineSearchCircle } from 'react-icons/hi';

export default function ThreatEmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-24 px-4 text-center select-none bg-surface/30 border border-border-color rounded-xl w-full">
      <div className="p-4 rounded-full bg-surface border border-border-color text-text-muted opacity-50 mb-5">
        <HiOutlineSearchCircle className="w-12 h-12 text-primary-blue animate-pulse" />
      </div>
      
      <h3 className="text-base font-bold text-text-primary mb-1">
        Start Indicator Investigation
      </h3>
      
      <p className="text-xs text-text-secondary max-w-sm leading-relaxed">
        Query threat intelligence records. Enter an IP address, domain name, or user identity above to scan the correlation database for compromise indicators.
      </p>
    </div>
  );
}
