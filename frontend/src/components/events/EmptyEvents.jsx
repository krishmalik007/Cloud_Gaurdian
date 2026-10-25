import React from 'react';
import { RiFileList3Line, RiRefreshLine } from 'react-icons/ri';
import { Button } from '../ui/Button';

export default function EmptyEvents({ onRefresh }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-border-color rounded-2xl bg-surface/10 max-w-xl mx-auto my-8 select-none">
      <div className="flex items-center justify-center w-14 h-14 rounded-full bg-primary-blue/10 border border-primary-blue/20 text-primary-blue mb-4">
        <RiFileList3Line className="w-7 h-7" />
      </div>
      <h3 className="text-base font-bold text-text-primary tracking-tight">
        No Cloud Events Found
      </h3>
      <p className="text-xs text-text-muted mt-2 max-w-sm leading-relaxed">
        No cloud log records matched your query. Adjust search filters or check your AWS SQS and S3 log ingestion pipelines.
      </p>
      {onRefresh && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          className="mt-5 flex items-center gap-2"
        >
          <RiRefreshLine className="w-4 h-4" />
          Refresh Event Stream
        </Button>
      )}
    </div>
  );
}
