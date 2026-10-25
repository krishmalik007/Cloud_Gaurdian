import { useQuery } from '@tanstack/react-query';
import { eventService } from '../services/eventService';

const getRefetchInterval = () => {
  try {
    const prefs = JSON.parse(localStorage.getItem('cg_settings_preferences') || '{"autoRefresh": true}');
    if (prefs.autoRefresh === false) return false;
  } catch (e) {}
  const val = parseInt(localStorage.getItem('cg_settings_refresh') || '15', 10);
  return val > 0 ? val * 1000 : false;
};

export const useEventsSearch = (filters = {}) => {
  return useQuery({
    queryKey: ['events', 'search', filters],
    queryFn: () => eventService.searchEvents(filters),
    keepPreviousData: true,
    refetchInterval: getRefetchInterval(),
  });
};

export const useEventDetails = (eventId) => {
  return useQuery({
    queryKey: ['events', 'details', eventId],
    queryFn: () => eventService.getEvent(eventId),
    enabled: !!eventId,
  });
};

export const useEventStats = () => {
  return useQuery({
    queryKey: ['events', 'stats'],
    queryFn: () => eventService.getStats(),
    refetchInterval: getRefetchInterval(),
  });
};
