import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { incidentService } from '../services/incidentService';

export const useIncidentsSearch = (filters = {}) => {
  return useQuery({
    queryKey: ['incidents', 'search', filters],
    queryFn: () => incidentService.searchIncidents(filters),
    keepPreviousData: true,
  });
};

export const useIncidentDetails = (incidentId) => {
  return useQuery({
    queryKey: ['incidents', 'details', incidentId],
    queryFn: () => incidentService.getIncident(incidentId),
    enabled: !!incidentId,
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
