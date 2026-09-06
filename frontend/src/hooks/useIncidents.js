import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { incidentService } from '../services/incidentService';

const getRefetchInterval = () => {
  try {
    const prefs = JSON.parse(localStorage.getItem('cg_settings_preferences') || '{"autoRefresh": true}');
    if (prefs.autoRefresh === false) return false;
  } catch(e) {}
  const val = parseInt(localStorage.getItem('cg_settings_refresh') || '30', 10);
  return val > 0 ? val * 1000 : false;
};

export const useIncidentsSearch = (filters = {}) => {
  return useQuery({
    queryKey: ['incidents', 'search', filters],
    queryFn: () => incidentService.searchIncidents(filters),
    keepPreviousData: true,
    refetchInterval: getRefetchInterval(),
  });
};

export const useIncidentDetails = (incidentId) => {
  return useQuery({
    queryKey: ['incidents', 'details', incidentId],
    queryFn: () => incidentService.getIncident(incidentId),
    enabled: !!incidentId,
    refetchInterval: getRefetchInterval(),
  });
};

export const useDeleteIncident = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: incidentService.deleteIncident,
    onSuccess: (data, incidentId) => {
      // Invalidate queries to refresh table data
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useUpdateIncidentStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, status }) => incidentService.updateStatus(incidentId, status),
    onSuccess: (data, { incidentId }) => {
      queryClient.invalidateQueries({ queryKey: ['incidents', 'details', incidentId] });
      queryClient.invalidateQueries({ queryKey: ['incidents', 'search'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useAddIncidentNote = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ incidentId, note }) => incidentService.addNote(incidentId, note),
    onSuccess: (data, { incidentId }) => {
      queryClient.invalidateQueries({ queryKey: ['incidents', 'details', incidentId] });
    },
  });
};
