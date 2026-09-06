import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/layout/PageHeader';
import IncidentDetailContent from '../../components/incidents/IncidentDetailContent';
import { ROUTES } from '../../constants/routes';

export default function IncidentDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={`Incident: ${id}`}
        subtitle="In-depth log analysis and audit timeline."
        onBack={() => navigate(ROUTES.INCIDENTS)}
        showBack={true}
      />
      <div className="bg-surface border border-border-color rounded-xl p-6 shadow-sm">
        <IncidentDetailContent incidentId={id} />
      </div>
    </div>
  );
}
