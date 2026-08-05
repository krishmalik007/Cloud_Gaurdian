import React from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';

export default function Profile() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Security Analyst Profile"
        subtitle="Review security credentials, active sessions, and keys."
      />
      <Card title="Module Status" subtitle="Pending Phase 5 implementation">
        <div className="py-12 text-center text-text-muted">
          Analyst details, password update form, and sessions overview will be loaded in Phase 5.
        </div>
      </Card>
    </div>
  );
}
