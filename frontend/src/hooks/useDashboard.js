import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';

const getRefetchInterval = () => {
  try {
    const prefs = JSON.parse(localStorage.getItem('cg_settings_preferences') || '{"autoRefresh": true}');
    if (prefs.autoRefresh === false) return false;
  } catch(e) {}
  const val = parseInt(localStorage.getItem('cg_settings_refresh') || '30', 10);
  return val > 0 ? val * 1000 : false;
};

export const useDashboardSummary = () => {
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: dashboardService.getSummary,
    refetchInterval: getRefetchInterval(),
  });
};

export const useDashboardProviderStats = () => {
  return useQuery({
    queryKey: ['dashboard', 'provider-stats'],
    queryFn: dashboardService.getProviderStats,
    refetchInterval: getRefetchInterval(),
  });
};

export const useDashboardRiskDistribution = () => {
  return useQuery({
    queryKey: ['dashboard', 'risk-distribution'],
    queryFn: dashboardService.getRiskDistribution,
    refetchInterval: getRefetchInterval(),
  });
};

export const useDashboardRecentIncidents = (limit = 10) => {
  return useQuery({
    queryKey: ['dashboard', 'recent-incidents', limit],
    queryFn: () => dashboardService.getRecentIncidents(limit),
    refetchInterval: getRefetchInterval(),
  });
};

export const useDashboardHealth = () => {
  return useQuery({
    queryKey: ['dashboard', 'health'],
    queryFn: dashboardService.getHealth,
    refetchInterval: getRefetchInterval(),
  });
};

// Combined hook for clean component usage
export const useDashboard = () => {
  const summaryQuery = useDashboardSummary();
  const providerStatsQuery = useDashboardProviderStats();
  const riskDistributionQuery = useDashboardRiskDistribution();
  const recentIncidentsQuery = useDashboardRecentIncidents();
  const healthQuery = useDashboardHealth();

  return {
    summary: summaryQuery.data,
    providerStats: providerStatsQuery.data,
    riskDistribution: riskDistributionQuery.data,
    recentIncidents: recentIncidentsQuery.data,
    health: healthQuery.data,
    
    isLoading: 
      summaryQuery.isLoading || 
      providerStatsQuery.isLoading || 
      riskDistributionQuery.isLoading || 
      recentIncidentsQuery.isLoading || 
      healthQuery.isLoading,
      
    isError: 
      summaryQuery.isError || 
      providerStatsQuery.isError || 
      riskDistributionQuery.isError || 
      recentIncidentsQuery.isError || 
      healthQuery.isError,

    refetchAll: () => {
      summaryQuery.refetch();
      providerStatsQuery.refetch();
      riskDistributionQuery.refetch();
      recentIncidentsQuery.refetch();
      healthQuery.refetch();
    }
  };
};
