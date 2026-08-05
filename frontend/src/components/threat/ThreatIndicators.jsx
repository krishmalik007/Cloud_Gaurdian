import React from 'react';
import { Card } from '../ui/Card';
import { HiOutlineCheckCircle, HiOutlineExclamationCircle } from 'react-icons/hi';

export default function ThreatIndicators({ result }) {
  const flags = [
    { label: 'Active watchlist check', flagged: result.enabled },
    { label: 'Intelligence feed match', flagged: result.malicious },
    { label: 'Elevated risk score mapping', flagged: ['CRITICAL', 'HIGH'].includes(String(result.severity).toUpperCase()) },
    { label: 'Campaign attribution identified', flagged: !!result.description && result.malicious },
  ];

  return (
    <Card title="Correlated Threat Indicators" className="bg-surface/30">
      <div className="flex flex-col gap-3 mt-3 text-left select-none">
        {flags.map((flag, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between p-2.5 bg-background/50 border border-border-color rounded-lg text-xs"
          >
            <span className="text-text-secondary">{flag.label}</span>
            <div className="flex items-center gap-1.5 font-semibold">
              {flag.flagged ? (
                <span className="text-red flex items-center gap-1">
                  <HiOutlineExclamationCircle className="w-4.5 h-4.5" />
                  FLAGGED
                </span>
              ) : (
                <span className="text-green flex items-center gap-1">
                  <HiOutlineCheckCircle className="w-4.5 h-4.5" />
                  CLEAN
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
