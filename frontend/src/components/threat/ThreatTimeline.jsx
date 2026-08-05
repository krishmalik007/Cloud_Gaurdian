import React from 'react';
import { Card } from '../ui/Card';
import { HiOutlineClock, HiOutlineShieldExclamation, HiOutlineCheck } from 'react-icons/hi';

export default function ThreatTimeline({ result }) {
  const isMalicious = result.malicious;

  return (
    <Card title="Intelligence Evaluation Trail" className="h-full bg-surface/30">
      <div className="flex flex-col gap-5 relative pl-6 border-l border-border-color mt-4 text-left select-none ml-2">
        {/* Step 1 */}
        <div className="relative">
          <div className="absolute -left-[37px] top-0 p-1 bg-surface border border-border-color rounded-full text-text-muted">
            <HiOutlineClock className="w-3.5 h-3.5" />
          </div>
          <div className="flex flex-col gap-0.5">
            <span className="text-xs font-bold text-text-primary">Query Initialized</span>
            <span className="text-[10px] text-text-muted">Target indicators extracted and prepared.</span>
          </div>
        </div>

        {/* Step 2 */}
        <div className="relative">
          <div className="absolute -left-[37px] top-0 p-1 bg-surface border border-border-color rounded-full text-text-muted">
            <HiOutlineClock className="w-3.5 h-3.5" />
          </div>
          <div className="flex flex-col gap-0.5">
            <span className="text-xs font-bold text-text-primary">Database Lookup Executed</span>
            <span className="text-[10px] text-text-muted">OpenSearch IOC records scanned for pattern matches.</span>
          </div>
        </div>

        {/* Step 3 */}
        <div className="relative">
          <div className={`absolute -left-[37px] top-0 p-1 border rounded-full ${
            isMalicious 
              ? 'bg-red/10 border-red/20 text-red' 
              : 'bg-green/10 border-green/20 text-green'
          }`}>
            {isMalicious ? <HiOutlineShieldExclamation className="w-3.5 h-3.5" /> : <HiOutlineCheck className="w-3.5 h-3.5" />}
          </div>
          <div className="flex flex-col gap-0.5">
            <span className="text-xs font-bold text-text-primary">Verdict Correlation Completed</span>
            <span className="text-[10px] text-text-muted">
              {isMalicious 
                ? 'Malicious watch flag detected in local threat feeds.' 
                : 'Zero threat matches detected in correlation database.'}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
