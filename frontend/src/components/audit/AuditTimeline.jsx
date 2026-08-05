import React from 'react';
import { HiOutlineClock, HiOutlineShieldCheck, HiOutlinePlay } from 'react-icons/hi';

export default function AuditTimeline({ timestamp }) {
  if (!timestamp) return null;

  const t = new Date(timestamp);
  const steps = [
    {
      title: 'Action Triggered',
      desc: 'User initiated administrative request.',
      time: t.toLocaleTimeString(),
      icon: HiOutlinePlay,
      color: 'text-primary-blue bg-primary-blue/10 border-primary-blue/20',
    },
    {
      title: 'Audit Log Ingested',
      desc: 'Security event registered in correlation logs.',
      time: new Date(t.getTime() + 800).toLocaleTimeString(),
      icon: HiOutlineClock,
      color: 'text-warning bg-warning/10 border-warning/20',
    },
    {
      title: 'Action Completed',
      desc: 'Backend processed task successfully.',
      time: new Date(t.getTime() + 1500).toLocaleTimeString(),
      icon: HiOutlineShieldCheck,
      color: 'text-green bg-green/10 border-green/20',
    },
  ];

  return (
    <div className="flex flex-col gap-6 relative pl-6 border-l border-border-color select-none ml-2">
      {steps.map((step, idx) => {
        const Icon = step.icon;
        return (
          <div key={idx} className="relative text-left">
            <div className={`absolute -left-[37px] top-0 p-1.5 rounded-full border flex items-center justify-center ${step.color}`}>
              <Icon className="w-4 h-4" />
            </div>
            
            <div className="flex flex-col gap-0.5">
              <div className="flex items-center justify-between gap-4">
                <span className="text-xs font-bold text-text-primary">
                  {step.title}
                </span>
                <span className="text-[10px] text-text-muted flex items-center gap-1">
                  <HiOutlineClock className="w-3 h-3" />
                  {step.time}
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
