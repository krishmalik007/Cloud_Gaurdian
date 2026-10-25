import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RiUploadCloud2Line, RiAlertLine, RiGitRepositoryPrivateLine, RiFileList3Line } from 'react-icons/ri';
import { Button } from '../ui/Button';
import { ROUTES } from '../../constants/routes';

export default function QuickActions() {
  const navigate = useNavigate();

  return (
    <div className="bg-surface border border-border-color rounded-xl p-6 flex flex-col justify-between h-full shadow-sm">
      <div className="flex flex-col gap-1 text-left mb-4 select-none">
        <h3 className="text-sm font-semibold text-text-primary tracking-tight">Quick Operations Actions</h3>
        <p className="text-[11px] text-text-muted">Direct shortcuts to critical security workflows.</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Button
          variant="outline"
          size="sm"
          icon={RiFileList3Line}
          onClick={() => navigate(ROUTES.EVENTS)}
          className="w-full text-xs"
        >
          Cloud Events
        </Button>
        
        <Button
          variant="outline"
          size="sm"
          icon={RiAlertLine}
          onClick={() => navigate(ROUTES.INCIDENTS)}
          className="w-full text-xs"
        >
          Incidents
        </Button>

        <Button
          variant="outline"
          size="sm"
          icon={RiUploadCloud2Line}
          onClick={() => navigate(ROUTES.UPLOAD_LOGS)}
          className="w-full text-xs"
        >
          Upload Logs
        </Button>

        <Button
          variant="outline"
          size="sm"
          icon={RiGitRepositoryPrivateLine}
          onClick={() => navigate(ROUTES.IOC_MANAGEMENT)}
          className="w-full text-xs"
        >
          IOC Registry
        </Button>
      </div>
    </div>
  );
}
