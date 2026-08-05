import React from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';

export default function IncidentDetails() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Incident Detail Analysis"
        subtitle="In-depth log analysis and audit timeline."
      />
      <Card title="Module Status" subtitle="Pending Phase 3 implementation">
        <div className="py-12 text-center text-text-muted">
          Detailed raw log viewers and telemetry charts will be loaded in Phase 3.
        </div>
      </Card>
    </div>
  );
}
