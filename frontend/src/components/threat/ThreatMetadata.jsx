import React from 'react';
import { Card } from '../ui/Card';

export default function ThreatMetadata({ result }) {
  return (
    <Card title="Threat Metadata Details" className="h-full bg-surface/30">
      <div className="flex flex-col gap-4 mt-3 text-left select-none">
        <div className="grid grid-cols-2 gap-4 border-b border-border-color/30 pb-3">
          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] font-bold text-text-muted uppercase">Target Value</span>
            <span className="font-mono text-xs font-semibold text-text-primary select-all">
              {result.value}
            </span>
          </div>
          
          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] font-bold text-text-muted uppercase">Indicator Type</span>
            <span className="text-xs font-semibold text-text-primary uppercase">
              {result.ioc_type}
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-1 border-b border-border-color/30 pb-3">
          <span className="text-[10px] font-bold text-text-muted uppercase">Intel Description</span>
          <p className="text-xs text-text-secondary leading-relaxed">
            {result.description || 'No campaign descriptions associated with this intelligence indicator.'}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] font-bold text-text-muted uppercase">Watchlist Created</span>
            <span className="text-xs font-semibold text-text-secondary">
              {result.created_at ? new Date(result.created_at).toLocaleString() : 'N/A'}
            </span>
          </div>

          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] font-bold text-text-muted uppercase">Risk Status</span>
            <span className="text-xs font-semibold text-text-secondary">
              {result.malicious ? 'Active Threat Vector' : 'White-listed / Unmatched'}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
