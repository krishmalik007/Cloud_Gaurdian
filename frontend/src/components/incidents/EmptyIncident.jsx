import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RiAlertLine } from 'react-icons/ri';
import { Button } from '../ui/Button';
import { ROUTES } from '../../constants/routes';

export default function EmptyIncident({ onRefresh }) {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center select-none bg-surface/30 border border-border-color rounded-xl w-full">
      <div className="p-4 rounded-full bg-surface border border-border-color text-text-muted opacity-60 mb-5 relative">
        <RiAlertLine className="w-12 h-12" />
        <span className="absolute top-3.5 right-3.5 w-2.5 h-2.5 rounded-full bg-red animate-ping" />
      </div>
      
      <h3 className="text-base font-bold text-text-primary mb-1">
        No Incidents Found
      </h3>
      
      <p className="text-xs text-text-secondary max-w-sm mb-6 leading-relaxed">
        We couldn't detect any security anomalies in OpenSearch. Ingest raw log files or trigger a manual scan to begin monitoring security events.
      </p>

      <div className="flex items-center gap-3">
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
        >
          Refresh Feeds
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={() => navigate(ROUTES.UPLOAD_LOGS)}
        >
          Upload Cloud Logs
        </Button>
      </div>
    </div>
  );
}
