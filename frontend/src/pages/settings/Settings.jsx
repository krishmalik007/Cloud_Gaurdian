import React from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';

export default function Settings() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="SOC Configuration Settings"
        subtitle="Manage alerts correlation settings, API thresholds, and notifications."
      />
      <Card title="Module Status" subtitle="Pending Phase 5 implementation">
        <div className="py-12 text-center text-text-muted">
          Platform configurations and variables parameters will be loaded in Phase 5.
        </div>
      </Card>
    </div>
  );
}
