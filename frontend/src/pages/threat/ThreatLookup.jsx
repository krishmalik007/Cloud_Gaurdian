import React from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';

export default function ThreatLookup() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Threat Intelligence Lookup"
        subtitle="Search reputation of IP addresses, domain names, and usernames."
      />
      <Card title="Module Status" subtitle="Pending Phase 5 implementation">
        <div className="py-12 text-center text-text-muted">
          Threat Intelligence search boxes and response cards will be loaded in Phase 5.
        </div>
      </Card>
    </div>
  );
}
