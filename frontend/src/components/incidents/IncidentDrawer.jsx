import React from 'react';
import { Drawer } from '../ui/Drawer';
import IncidentDetailContent from './IncidentDetailContent';

export default function IncidentDrawer({ isOpen, onClose, incidentId }) {
  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={incidentId ? `Incident: ${incidentId}` : 'Incident Details'}
      size="xl"
    >
      {incidentId && <IncidentDetailContent incidentId={incidentId} />}
    </Drawer>
  );
}
