import React, { useState, useEffect } from 'react';
import { useIncidentDetails, useUpdateIncidentStatus, useAddIncidentNote } from '../../hooks/useIncidents';
import { Skeleton } from '../ui/Skeleton';
import { Badge } from '../ui/Badge';
import IncidentSeverityBadge from './IncidentSeverityBadge';
import IncidentStatusBadge from './IncidentStatusBadge';
import IncidentTimeline from './IncidentTimeline';
import { 
  HiOutlineTerminal, 
  HiOutlineDatabase, 
  HiOutlineUser, 
  HiOutlineInformationCircle,
  HiOutlineShieldCheck,
  HiOutlineClipboardList,
  HiOutlineChatAlt2,
  HiOutlineExclamationCircle
} from 'react-icons/hi';


export default function IncidentDetailContent({ incidentId }) {
  const { data: incident, isLoading, isError } = useIncidentDetails(incidentId);
  const updateStatusMutation = useUpdateIncidentStatus();
  const addNoteMutation = useAddIncidentNote();

  const [newNote, setNewNote] = useState('');
  const [detailLevel, setDetailLevel] = useState('standard');

  useEffect(() => {
    try {
      const prefs = JSON.parse(localStorage.getItem('cg_settings_preferences') || '{}');
      if (prefs.detailLevel) {
        setDetailLevel(prefs.detailLevel);
      }
    } catch (e) {}
  }, []);
  
  const handleStatusChange = (e) => {
    const newStatus = e.target.value;
    updateStatusMutation.mutate({ incidentId, status: newStatus });
  };

  const handleAddNote = () => {
    if (!newNote.trim()) return;
    addNoteMutation.mutate({ incidentId, note: newNote }, {
      onSuccess: () => setNewNote('')
    });
  };

  const getAttentionColor = (attention) => {
    if (attention === 'REQUIRED' || attention === 'IMMEDIATE ATTENTION') return 'text-red bg-red/10 border-red/20';
    if (attention === 'REVIEW RECOMMENDED') return 'text-orange bg-orange/10 border-orange/20';
    return 'text-green bg-green/10 border-green/20';
  };

  const getProviderVariant = (provider) => {
    const p = String(provider).toUpperCase();
    if (p === 'AWS') return 'warning';
    if (p === 'AZURE') return 'info';
    if (p === 'GCP') return 'purple';
    return 'muted';
  };

  return (
    <>
      {isLoading ? (
        <div className="flex flex-col gap-6 w-full">
          <Skeleton className="h-20" />
          <Skeleton className="h-40" />
          <Skeleton className="h-32" />
        </div>
      ) : isError || !incident ? (
        <div className="text-center py-12 text-text-muted">
          Failed to fetch incident details. Please check connection.
        </div>
      ) : (
        <div className="flex flex-col gap-6 text-left pb-10 select-none">
          
          {/* 1. Incident Header */}
          <div className="flex flex-col md:flex-row gap-4 p-4 bg-background/40 border border-border-color rounded-xl justify-between items-start md:items-center">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-3">
                <span className="font-semibold text-text-secondary text-sm">Status:</span>
                <select 
                  value={incident.status}
                  onChange={handleStatusChange}
                  disabled={updateStatusMutation.isLoading}
                  className="bg-surface border border-border-color rounded-md px-2 py-1 text-xs text-text-primary focus:outline-none focus:border-primary-blue cursor-pointer"
                >
                  <option value="OPEN">OPEN</option>
                  <option value="INVESTIGATING">INVESTIGATING</option>
                  <option value="RESOLVED">RESOLVED</option>
                </select>
                {updateStatusMutation.isLoading && <span className="text-[10px] text-text-muted">Updating...</span>}
              </div>
              <div className="flex gap-4 text-xs font-semibold">
                <div className="flex items-center gap-1.5">
                  <span className="text-text-muted">Risk Level:</span>
                  <IncidentSeverityBadge severity={incident.risk_level} size="sm" />
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="text-text-muted">Risk Score:</span>
                  <span className="text-text-primary">{incident.risk_score}/100</span>
                </div>
                {incident.threat_score !== undefined && (
                  <div className="flex items-center gap-1.5">
                    <span className="text-text-muted">Threat Score:</span>
                    <span className="text-text-primary">{incident.threat_score}/100</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className={`flex flex-col items-end gap-1 p-3 border rounded-lg ${getAttentionColor(incident.analyst_attention)}`}>
              <span className="text-[10px] uppercase font-bold tracking-wider opacity-80">Analyst Attention</span>
              <span className="font-bold text-sm">{incident.analyst_attention || 'NOT REQUIRED'}</span>
            </div>
          </div>

          {/* 2. Why This Incident Exists */}
          {incident.alerts && incident.alerts.length > 0 && (
             <div className="flex flex-col gap-2 p-4 bg-surface/30 border border-border-color rounded-xl">
               <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
                 <HiOutlineExclamationCircle className="w-4.5 h-4.5 text-primary-blue" />
                 Why This Incident Exists
               </h4>
               <ul className="list-disc list-inside text-xs text-text-secondary mt-1 flex flex-col gap-1.5">
                 {incident.alerts.map((alert, idx) => (
                   <li key={idx}>
                     <span className="font-semibold text-text-primary">{alert.alert_type || alert.rule_name}:</span> {alert.description}
                   </li>
                 ))}
               </ul>
             </div>
          )}

          {/* 3. Event Summary */}
          <div className="flex flex-col gap-3 p-4 border border-border-color rounded-xl bg-surface/20">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
              <HiOutlineClipboardList className="w-4.5 h-4.5 text-primary-blue" />
              Event Summary
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs mt-1">
              <div className="flex flex-col gap-1">
                <span className="text-text-muted font-medium">Provider</span>
                <Badge variant={getProviderVariant(incident.provider)} size="sm" className="w-max">
                  {String(incident.provider).toUpperCase()}
                </Badge>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-text-muted font-medium">Event Name</span>
                <span className="font-semibold text-text-primary">{incident.event_summary?.event_name || '-'}</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-text-muted font-medium">Identity / User</span>
                <span className="font-semibold text-text-primary flex items-center gap-1.5">
                  <HiOutlineUser className="w-3.5 h-3.5 text-text-muted" />
                  {incident.username || '-'}
                </span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-text-muted font-medium">Source IP</span>
                <span className="font-mono text-text-primary">{incident.event_summary?.source_ip || '-'}</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-text-muted font-medium">Region</span>
                <span className="font-semibold text-text-primary">{incident.event_summary?.region || '-'}</span>
              </div>
              <div className="flex flex-col gap-1 md:col-span-2">
                <span className="text-text-muted font-medium">Timestamp</span>
                <span className="font-semibold text-text-secondary">{incident.event_summary?.timestamp ? new Date(incident.event_summary.timestamp).toLocaleString() : '-'}</span>
              </div>
            </div>
          </div>

          {/* 4. Correlated Activity */}
          {detailLevel === 'detailed' && (
          <div className="flex flex-col gap-3 p-4 border border-border-color rounded-xl bg-surface/20">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
              <HiOutlineDatabase className="w-4.5 h-4.5 text-primary-blue" />
              Correlated Activity
            </h4>
            {incident.alerts && incident.alerts.some(a => a.related_events && a.related_events.length > 0) ? (
              <div className="flex flex-col gap-3 mt-1 text-xs">
                {incident.alerts.filter(a => a.related_events && a.related_events.length > 0).map((alert, idx) => (
                  <div key={idx} className="flex flex-col gap-2">
                    <span className="font-semibold text-text-secondary">{alert.alert_type || alert.rule_name} related events:</span>
                    <div className="overflow-x-auto rounded-lg border border-border-color">
                      <table className="w-full text-left border-collapse">
                        <thead className="bg-background/80 text-[10px] uppercase text-text-muted">
                          <tr>
                            <th className="px-3 py-2 font-semibold">Event</th>
                            <th className="px-3 py-2 font-semibold">Time</th>
                            <th className="px-3 py-2 font-semibold">Source IP</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border-color bg-surface/50">
                          {alert.related_events.map((evt, eIdx) => (
                            <tr key={eIdx}>
                              <td className="px-3 py-2 text-text-primary font-medium">{evt.event_name || evt.event_type}</td>
                              <td className="px-3 py-2 text-text-secondary">{evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : '-'}</td>
                              <td className="px-3 py-2 text-text-primary font-mono">{evt.source_ip || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <span className="text-xs text-text-muted italic mt-1">No related suspicious activity identified.</span>
            )}
          </div>
          )}

          {/* 5. Threat Intelligence */}
          {incident.threat_level !== undefined && (
            <div className="flex flex-col gap-2 p-4 border border-border-color rounded-xl bg-surface/20">
              <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
                <HiOutlineShieldCheck className="w-4.5 h-4.5 text-primary-blue" />
                Threat Intelligence
              </h4>
              <div className="text-xs mt-1">
                {incident.threat_score > 0 ? (
                  <div className="flex flex-col gap-1.5">
                    <div className="flex gap-2">
                      <span className="text-text-muted font-medium">Match Level:</span>
                      <IncidentSeverityBadge severity={incident.threat_level} size="sm" />
                    </div>
                    {incident.threat_tags && incident.threat_tags.length > 0 && (
                      <div className="flex gap-2 items-center">
                        <span className="text-text-muted font-medium">Tags:</span>
                        <div className="flex flex-wrap gap-1">
                          {incident.threat_tags.map((tag, idx) => (
                            <span key={idx} className="bg-background/80 border border-border-color px-2 py-0.5 rounded text-[10px] text-text-secondary">{tag}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <span className="text-text-muted italic">No threat intelligence match.</span>
                )}
              </div>
            </div>
          )}

          {/* 6 & 7. XDR Assessment & Recommended Action */}
          <div className="flex flex-col gap-4 p-4 border border-border-color rounded-xl bg-surface/20">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
              <HiOutlineShieldCheck className="w-4.5 h-4.5 text-primary-blue" />
              XDR Assessment
            </h4>
            <div className="flex flex-col gap-3 text-xs mt-1">
              <div className="flex flex-col gap-1">
                <span className="text-text-muted font-medium">Assessment:</span>
                <span className="font-semibold text-text-primary">{incident.xdr_assessment || 'No automated assessment available.'}</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-text-muted font-medium">Recommended Analyst Action:</span>
                <span className="font-semibold text-text-secondary">
                  {incident.analyst_attention === 'REQUIRED' || incident.analyst_attention === 'IMMEDIATE ATTENTION' 
                    ? 'Investigate the related activity, identity, and source to determine whether actions were authorized.'
                    : incident.analyst_attention === 'REVIEW RECOMMENDED' 
                    ? 'Review the event summary to confirm it aligns with expected behavior.'
                    : 'No immediate investigation required. Incident can be resolved if no further anomalies exist.'}
                </span>
              </div>
            </div>
          </div>

          {/* 8. Investigation Notes */}
          <div className="flex flex-col gap-4 p-4 border border-border-color rounded-xl bg-surface/20">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
              <HiOutlineChatAlt2 className="w-4.5 h-4.5 text-primary-blue" />
              Investigation Notes
            </h4>
            <div className="flex flex-col gap-3 mt-1">
              {incident.notes && incident.notes.length > 0 ? (
                <div className="flex flex-col gap-3">
                  {incident.notes.map((n, idx) => (
                    <div key={idx} className="flex flex-col p-3 bg-background/50 rounded-lg border border-border-color gap-1.5">
                      <div className="flex justify-between items-center text-[10px] text-text-muted border-b border-border-color/50 pb-1.5">
                        <span className="font-semibold text-text-primary flex items-center gap-1.5"><HiOutlineUser/> {n.author}</span>
                        <span>{new Date(n.timestamp).toLocaleString()}</span>
                      </div>
                      <p className="text-xs text-text-secondary pt-1 whitespace-pre-wrap">{n.note}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <span className="text-xs text-text-muted italic">No investigation notes added yet.</span>
              )}
              
              <div className="flex flex-col gap-2 mt-2">
                <textarea 
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Add an investigation note..."
                  className="w-full bg-surface border border-border-color rounded-lg p-2.5 text-xs text-text-primary focus:outline-none focus:border-primary-blue resize-none h-20"
                />
                <div className="flex justify-end">
                  <button 
                    onClick={handleAddNote}
                    disabled={addNoteMutation.isLoading || !newNote.trim()}
                    className="px-4 py-1.5 bg-primary-blue hover:bg-primary-blue/90 disabled:opacity-50 text-white text-xs font-bold rounded-md transition-colors"
                  >
                    {addNoteMutation.isLoading ? 'Adding...' : 'Add Note'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 9. Chronological Incident Lifecycle */}
          <div className="flex flex-col gap-4 mt-2">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
              <HiOutlineInformationCircle className="w-4.5 h-4.5 text-primary-blue" />
              Operational Triage Timeline
            </h4>
            <div className="pl-2 pt-2">
              <IncidentTimeline 
                createdTime={incident.created_at} 
                status={incident.status}
                notes={incident.notes}
                updatedAt={incident.updated_at}
              />
            </div>
          </div>

          {/* 10. Raw Log Telemetry Viewer */}
          {incident.raw_log && detailLevel === 'detailed' && (
            <div className="flex flex-col gap-3 mt-4">
              <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
                <HiOutlineTerminal className="w-4.5 h-4.5 text-primary-blue" />
                Raw Telemetry Stream
              </h4>
              <div className="bg-background/80 border border-border-color rounded-xl p-4 font-mono text-[10px] text-green overflow-x-auto select-all max-h-60 max-w-full">
                <pre>{JSON.stringify(incident.raw_log, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
}
