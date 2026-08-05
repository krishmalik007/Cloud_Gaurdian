import React from 'react';
import { HiOutlineClock, HiOutlineCube, HiOutlineShieldCheck, HiOutlineEye } from 'react-icons/hi';

export default function IncidentTimeline({ createdTime }) {
  const steps = [
    {
      title: 'Log Ingested',
      desc: 'Raw telemetry log stream normalized and parsed.',
      icon: HiOutlineCube,
      time: createdTime,
      color: 'text-primary-blue bg-primary-blue/10 border-primary-blue/20',
    },
    {
      title: 'Correlation Completed',
      desc: 'Indicators matched against threat intelligence databases.',
      icon: HiOutlineShieldCheck,
      time: new Date(new Date(createdTime).getTime() + 1200).toISOString(),
      color: 'text-green bg-green/10 border-green/20',
    },
    {
      title: 'Alert Triage Initiated',
      desc: 'Incident status initialized as OPEN and assigned to SOC queue.',
      icon: HiOutlineEye,
      time: new Date(new Date(createdTime).getTime() + 2400).toISOString(),
      color: 'text-red bg-red/10 border-red/20',
    },
  ];

  return (
    <div className="flex flex-col gap-6 relative pl-6 border-l border-border-color select-none">
      {steps.map((step, idx) => {
        const Icon = step.icon;
        return (
          <div key={idx} className="relative text-left">
            {/* Timeline node icon indicator */}
            <div className={`absolute -left-[37px] top-0 p-1.5 rounded-full border flex items-center justify-center ${step.color}`}>
              <Icon className="w-4 h-4" />
            </div>
            
            <div className="flex flex-col gap-1">
              <div className="flex items-center justify-between gap-4">
                <span className="text-xs font-bold text-text-primary">
                  {step.title}
                </span>
                <span className="text-[10px] text-text-muted flex items-center gap-1">
                  <HiOutlineClock className="w-3 h-3" />
                  {new Date(step.time).toLocaleTimeString(undefined, {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                  })}
                </span>
              </div>
              <p className="text-[11px] text-text-secondary">
                {step.desc}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
