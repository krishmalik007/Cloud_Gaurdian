import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../services/dashboardService';

export const useDashboardSummary = () => {
  return useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: dashboardService.getSummary,
    refetchInterval: 15000, // refresh every 15s for live SOC updates
  });
};

export const useDashboardProviderStats = () => {
  return useQuery({
    queryKey: ['dashboard', 'provider-stats'],
    queryFn: dashboardService.getProviderStats,
    refetchInterval: 30000,
  });
};

export const useDashboardRiskDistribution = () => {
  return useQuery({
    queryKey: ['dashboard', 'risk-distribution'],
    queryFn: dashboardService.getRiskDistribution,
    refetchInterval: 30000,
  });
};

export const useDashboardRecentIncidents = (limit = 10) => {
  return useQuery({
    queryKey: ['dashboard', 'recent-incidents', limit],
    queryFn: () => dashboardService.getRecentIncidents(limit),
    refetchInterval: 15000,
  });
};

export const useDashboardHealth = () => {
  return useQuery({
    queryKey: ['dashboard', 'health'],
    queryFn: dashboardService.getHealth,
    refetchInterval: 30000,
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
