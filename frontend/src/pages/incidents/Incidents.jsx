import React from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';

export default function Incidents() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Incident Operations Center"
        subtitle="View, triage, and manage aggregated security events."
      />
      <Card title="Module Status" subtitle="Pending Phase 3 implementation">
        <div className="py-12 text-center text-text-muted">
          Incident management table and telemetry details will be loaded in Phase 3.
        </div>
      </Card>
    </div>
  );
}
