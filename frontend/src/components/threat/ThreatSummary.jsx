import React from 'react';
import { Card } from '../ui/Card';
import ThreatRiskBadge from './ThreatRiskBadge';
import { Badge } from '../ui/Badge';
import { HiOutlineShieldCheck, HiOutlineEye, HiOutlineServer, HiOutlineClock } from 'react-icons/hi';

export default function ThreatSummary({ result }) {
  const isMalicious = result.malicious;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 select-none w-full">
      {/* Verdict Card */}
      <Card title="Threat Verdict" className="!p-4 bg-surface/30">
        <div className="flex items-center justify-between mt-2">
          <Badge variant={isMalicious ? 'danger' : 'success'} size="md">
            {isMalicious ? 'MALICIOUS CORRELATION' : 'CLEAN / VERIFIED'}
          </Badge>
          <div className="text-text-muted opacity-30">
            <HiOutlineShieldCheck className="w-5 h-5" />
          </div>
        </div>
      </Card>

      {/* Severity Card */}
      <Card title="Watchlist Severity" className="!p-4 bg-surface/30">
        <div className="flex items-center justify-between mt-2">
          <ThreatRiskBadge severity={result.severity || 'LOW'} />
          <div className="text-text-muted opacity-30">
            <HiOutlineEye className="w-5 h-5" />
          </div>
        </div>
      </Card>

      {/* Source Feed */}
      <Card title="Intelligence Source" className="!p-4 bg-surface/30">
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs font-bold text-text-primary uppercase">
            {result.source || 'DATABASE'}
          </span>
          <div className="text-text-muted opacity-30">
            <HiOutlineServer className="w-5 h-5" />
          </div>
        </div>
      </Card>

      {/* Ingestion Status */}
      <Card title="Watchlist Flag" className="!p-4 bg-surface/30">
        <div className="flex items-center justify-between mt-2">
          <Badge variant={result.enabled ? 'danger' : 'muted'} size="sm">
            {result.enabled ? 'ACTIVE BLOCKLIST' : 'INACTIVE'}
          </Badge>
          <div className="text-text-muted opacity-30">
            <HiOutlineClock className="w-5 h-5" />
          </div>
        </div>
      </Card>
    </div>
  );
}
