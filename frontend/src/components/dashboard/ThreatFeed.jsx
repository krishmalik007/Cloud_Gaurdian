import React from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { RiRadarLine } from 'react-icons/ri';

export default function ThreatFeed({ iocs = [], loading = false }) {
  const getSeverityVariant = (severity) => {
    const s = String(severity).toUpperCase();
    if (s === 'CRITICAL' || s === 'HIGH') return 'danger';
    if (s === 'MEDIUM') return 'warning';
    return 'info';
  };

  return (
    <Card
      title="Threat Feed"
      subtitle="Live Indicators of Compromise registered in correlation engine"
      headerAction={<RiRadarLine className="text-primary-blue animate-pulse w-5 h-5" />}
    >
      <div className="flex flex-col gap-3 mt-4 h-[200px] overflow-y-auto w-full pr-1">
        {loading ? (
          Array.from({ length: 3 }).map((_, idx) => (
            <div
              key={idx}
              className="h-12 w-full bg-surface border border-border-color rounded-lg animate-pulse"
            />
          ))
        ) : iocs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-4">
            <span className="text-xs font-semibold text-text-muted">
              No recent threat activity available
            </span>
            <span className="text-[10px] text-text-muted mt-0.5">
              Active IOC database is empty.
            </span>
          </div>
        ) : (
          iocs.map((ioc, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 rounded-lg border border-border-color bg-background/20"
            >
              <div className="flex flex-col text-left gap-1">
                <span className="font-mono text-xs font-semibold text-text-primary">
                  {ioc.value}
                </span>
                <span className="text-[10px] text-text-muted font-medium uppercase">
                  Indicator Type: {ioc.type}
                </span>
              </div>
              
              <Badge variant={getSeverityVariant(ioc.severity)} size="sm">
                {String(ioc.severity).toUpperCase()}
              </Badge>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
