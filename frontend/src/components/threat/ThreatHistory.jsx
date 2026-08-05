import React from 'react';
import { Card } from '../ui/Card';
import { HiOutlineClock } from 'react-icons/hi';
import { Badge } from '../ui/Badge';

export default function ThreatHistory({ history = [], onHistoryClick }) {
  if (history.length === 0) return null;

  return (
    <Card title="Current Session History" className="bg-surface/30">
      <div className="flex flex-col gap-2 mt-3 text-left max-h-56 overflow-y-auto pr-1">
        {history.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onHistoryClick(item.type, item.value)}
            className="w-full flex items-center justify-between p-2.5 bg-background border border-border-color rounded-lg hover:border-primary-blue hover:bg-surface/30 transition-all cursor-pointer text-left select-none text-xs"
          >
            <div className="flex flex-col gap-0.5">
              <span className="font-mono text-text-primary font-semibold truncate max-w-[150px]">
                {item.value}
              </span>
              <span className="text-[9px] text-text-muted uppercase">Type: {item.type}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Badge variant={item.malicious ? 'danger' : 'success'} size="sm">
                {item.malicious ? 'FLAGGED' : 'CLEAN'}
              </Badge>
              <HiOutlineClock className="w-3.5 h-3.5 text-text-muted opacity-50" />
            </div>
          </button>
        ))}
      </div>
    </Card>
  );
}
