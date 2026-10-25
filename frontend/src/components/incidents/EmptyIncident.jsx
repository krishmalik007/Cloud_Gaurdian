import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RiAlertLine, RiFileList3Line } from 'react-icons/ri';
import { Button } from '../ui/Button';
import { ROUTES } from '../../constants/routes';

export default function EmptyIncident({ onRefresh, onSwitchToEvents }) {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center select-none bg-surface/30 border border-border-color rounded-xl w-full">
      <div className="p-4 rounded-full bg-surface border border-border-color text-text-muted opacity-60 mb-5 relative">
        <RiAlertLine className="w-12 h-12" />
        <span className="absolute top-3.5 right-3.5 w-2.5 h-2.5 rounded-full bg-green" />
      </div>
      
      <h3 className="text-base font-bold text-text-primary mb-1">
        No Security Incidents Detected
      </h3>
      
      <p className="text-xs text-text-secondary max-w-md mb-6 leading-relaxed">
        All analyzed telemetry logs are currently classified as routine informational events or operational health activity. Ingested events are continuously stored in the OpenSearch events repository.
      </p>

      <div className="flex flex-wrap items-center justify-center gap-3">
        {onSwitchToEvents ? (
          <Button
            variant="primary"
            size="sm"
            onClick={onSwitchToEvents}
            className="flex items-center gap-2"
          >
            <RiFileList3Line className="w-4 h-4" />
            View Ingested Cloud Events
          </Button>
        ) : (
          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate(ROUTES.EVENTS)}
            className="flex items-center gap-2"
          >
            <RiFileList3Line className="w-4 h-4" />
            View Ingested Cloud Events
          </Button>
        )}
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
        >
          Refresh Feeds
        </Button>
      </div>
    </div>
  );
}
