import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { logService } from '../services/logService';

export const useLogUpload = () => {
  const queryClient = useQueryClient();
  const [history, setHistory] = useState(() => {
    try {
      const stored = sessionStorage.getItem('cg_upload_history');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const uploadMutation = useMutation({
    mutationFn: logService.uploadLog,
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['audit'] });

      const newEntry = {
        timestamp: new Date().toISOString(),
        provider: variables.provider,
        status: 'SUCCESS',
        incidentId: data?.incident?.incident_id || 'N/A',
      };
      const updated = [newEntry, ...history].slice(0, 10);
      setHistory(updated);
      try {
        sessionStorage.setItem('cg_upload_history', JSON.stringify(updated));
      } catch (e) {
        // ignore
      }
    },
    onError: (error, variables) => {
      const newEntry = {
        timestamp: new Date().toISOString(),
        provider: variables.provider || 'UNKNOWN',
        status: 'FAILED',
        incidentId: null,
      };
      const updated = [newEntry, ...history].slice(0, 10);
      setHistory(updated);
      try {
        sessionStorage.setItem('cg_upload_history', JSON.stringify(updated));
      } catch (e) {
        // ignore
      }
    }
  });

  const clearHistory = () => {
    setHistory([]);
    sessionStorage.removeItem('cg_upload_history');
  };

  return {
    uploadMutation,
    history,
    clearHistory
  };
};
export default useLogUpload;
