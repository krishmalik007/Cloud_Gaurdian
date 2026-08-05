import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useIncidentsSearch } from '../../hooks/useIncidents';
import { HiOutlineBell as HiOutlineBellIcon, HiOutlineX } from 'react-icons/hi';
import { Button } from '../ui/Button';

export default function NotificationCenter() {
  const navigate = useNavigate();
  const { data } = useIncidentsSearch({ size: 5 });
  const incidents = data?.incidents || [];

  const [isOpen, setIsOpen] = useState(false);
  const [readIds, setReadIds] = useState(() => {
    try {
      const stored = localStorage.getItem('cg_read_notifications');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const unreadIncidents = incidents.filter(inc => !readIds.includes(inc.incident_id));
  const hasUnread = unreadIncidents.length > 0;

  const handleMarkAllRead = () => {
    const allIds = incidents.map(inc => inc.incident_id);
    const updated = Array.from(new Set([...readIds, ...allIds]));
    setReadIds(updated);
    localStorage.setItem('cg_read_notifications', JSON.stringify(updated));
  };

  const handleItemClick = (incidentId) => {
    // Add to read list
    if (!readIds.includes(incidentId)) {
      const updated = [...readIds, incidentId];
      setReadIds(updated);
      localStorage.setItem('cg_read_notifications', JSON.stringify(updated));
    }
    setIsOpen(false);
    navigate(`/incidents/${incidentId}`);
  };

  // Close dropdown on click outside
  useEffect(() => {
    if (!isOpen) return;
    const handleOutside = () => setIsOpen(false);
    document.addEventListener('click', handleOutside);
    return () => document.removeEventListener('click', handleOutside);
  }, [isOpen]);

  return (
    <div className="relative" onClick={(e) => e.stopPropagation()}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-text-muted hover:text-text-primary hover:bg-surface/50 rounded-lg transition-colors cursor-pointer border border-transparent hover:border-border-color focus:outline-none"
        aria-label="Notification Center"
      >
        <HiOutlineBellIcon className="w-5 h-5" />
        {hasUnread && (
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red animate-ping" />
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-surface border border-border-color rounded-xl shadow-2xl overflow-hidden z-50 animate-fade-in text-left select-none">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border-color bg-background/50">
            <span className="text-xs font-bold text-text-primary uppercase tracking-wider">
              Security Notifications
            </span>
            {hasUnread && (
              <button
                onClick={handleMarkAllRead}
                className="text-[10px] text-primary-blue hover:underline font-semibold cursor-pointer"
              >
                Mark all read
              </button>
            )}
          </div>

          <div className="max-h-72 overflow-y-auto flex flex-col">
            {incidents.length === 0 ? (
              <div className="py-10 text-center text-xs text-text-muted flex flex-col items-center justify-center gap-2">
                <HiOutlineBellIcon className="w-8 h-8 opacity-20" />
                <span>No active notifications.</span>
              </div>
            ) : (
              incidents.map((inc) => {
                const isRead = readIds.includes(inc.incident_id);
                return (
                  <button
                    key={inc.incident_id}
                    onClick={() => handleItemClick(inc.incident_id)}
                    className={`w-full p-3.5 border-b border-border-color/50 text-left transition-colors hover:bg-background/40 flex items-start gap-2.5 cursor-pointer outline-none ${
                      !isRead ? 'bg-primary-blue/5' : ''
                    }`}
                  >
                    <span className={`w-1.5 h-1.5 mt-1.5 rounded-full shrink-0 ${!isRead ? 'bg-primary-blue' : 'bg-transparent'}`} />
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[11px] font-bold text-text-primary">
                        Incident Generated ({inc.provider})
                      </span>
                      <p className="text-[10px] text-text-secondary truncate max-w-[220px]">
                        Severity: {inc.risk_level} | Risk Score: {inc.risk_score}
                      </p>
                      <span className="text-[9px] text-text-muted">
                        {new Date(inc.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  </button>
                );
              })
            )}
          </div>

          <div className="p-2 border-t border-border-color bg-background/50 text-center">
            <button
              onClick={() => { setIsOpen(false); navigate('/incidents'); }}
              className="text-[10px] text-text-secondary hover:text-text-primary font-semibold transition-colors w-full cursor-pointer py-1"
            >
              View All Ingested Incidents
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
