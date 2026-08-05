import React from 'react';
import ThreatSummary from './ThreatSummary';
import ThreatMetadata from './ThreatMetadata';
import ThreatTimeline from './ThreatTimeline';
import ThreatIndicators from './ThreatIndicators';
import { Card } from '../ui/Card';
import { HiOutlineTerminal } from 'react-icons/hi';

export default function ThreatResultCard({ result }) {
  return (
    <div className="flex flex-col gap-6 w-full mt-4 select-none">
      {/* High level metrics cards row */}
      <ThreatSummary result={result} />

      {/* Main Analysis Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
        {/* Left Column: Metadata */}
        <ThreatMetadata result={result} />
        
        {/* Right Column: Evaluation timeline */}
        <ThreatTimeline result={result} />
      </div>

      {/* Indicators and raw logs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
        <ThreatIndicators result={result} />

        {/* Raw response */}
        <Card title="Raw Intelligence Response" className="bg-surface/30">
          <div className="flex items-center gap-2 text-xs font-bold text-text-primary uppercase tracking-wider mb-3">
            <HiOutlineTerminal className="w-4 h-4 text-primary-blue" />
            Raw Payload JSON
          </div>
          <div className="bg-background/80 border border-border-color rounded-xl p-4 font-mono text-[10px] text-green overflow-x-auto select-all max-h-56 max-w-full text-left">
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        </Card>
      </div>
    </div>
  );
}
