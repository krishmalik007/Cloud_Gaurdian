import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDashboard } from '../../hooks/useDashboard';
import { useAuth } from '../../context/AuthContext';
import API from '../../services/api';

// Components
import WelcomeCard from '../../components/dashboard/WelcomeCard';
import QuickActions from '../../components/dashboard/QuickActions';
import StatCard from '../../components/dashboard/StatCard';
import IncidentTrendChart from '../../components/dashboard/IncidentTrendChart';
import RiskDistributionChart from '../../components/dashboard/RiskDistributionChart';
import ProviderChart from '../../components/dashboard/ProviderChart';
import RecentIncidents from '../../components/dashboard/RecentIncidents';
import SystemHealth from '../../components/dashboard/SystemHealth';
import ThreatFeed from '../../components/dashboard/ThreatFeed';

// Icons
import { RiAlertLine, RiBroadcastLine, RiUserSharedLine } from 'react-icons/ri';

export default function Dashboard() {
  const { user } = useAuth();
  const {
    summary,
    providerStats,
    riskDistribution,
    recentIncidents,
    health,
    isLoading,
    isError,
  } = useDashboard();

  // Load Active Users count if current user is ADMIN
  const { data: usersData, isLoading: loadingUsers } = useQuery({
    queryKey: ['admin', 'users-count'],
    queryFn: async () => {
      const response = await API.get('/users/');
      return response.data;
    },
    enabled: user?.role === 'ADMIN',
  });

  // Load IOC list for Threat Feed
  const { data: iocsData, isLoading: loadingIocs } = useQuery({
    queryKey: ['threat', 'iocs-feed'],
    queryFn: async () => {
      const response = await API.get('/iocs/');
      return response.data;
    },
  });

  const activeUsersCount = usersData?.users?.filter((u) => u.enabled).length || 1;
  
  // Calculate specific risk counts
  const criticalCount = riskDistribution?.find(
    (r) => String(r.risk_level).toUpperCase() === 'CRITICAL'
  )?.count || 0;

  const highCount = riskDistribution?.find(
    (r) => String(r.risk_level).toUpperCase() === 'HIGH'
  )?.count || summary?.high_risk || 0;

  return (
    <div className="flex flex-col gap-6 w-full animate-fade-in">
      {/* Welcome & Quick Actions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <WelcomeCard />
        </div>
        <div>
          <QuickActions />
        </div>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Correlated Incidents"
          value={summary?.total_incidents || 0}
          icon={RiAlertLine}
          variant="info"
          loading={isLoading}
          trend={{ type: 'down', value: '4.8%' }}
        />
        <StatCard
          title="Critical Security Alerts"
          value={criticalCount}
          icon={RiAlertLine}
          variant="danger"
          loading={isLoading}
          trend={{ type: 'up', value: '1.2%' }}
        />
        <StatCard
          title="High Severity Alerts"
          value={highCount}
          icon={RiAlertLine}
          variant="warning"
          loading={isLoading}
          trend={{ type: 'down', value: '8.4%' }}
        />
        <StatCard
          title="Active Analyst Sessions"
          value={activeUsersCount}
          icon={RiUserSharedLine}
          variant="success"
          loading={isLoading || (user?.role === 'ADMIN' && loadingUsers)}
        />
      </div>

      {/* Analytics Visualization Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <IncidentTrendChart data={recentIncidents} loading={isLoading} />
        <RiskDistributionChart data={riskDistribution} loading={isLoading} />
        <ProviderChart data={providerStats} loading={isLoading} />
      </div>

      {/* Bottom Grid: Recent Incidents, System status, Threat Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Incident list */}
        <div className="lg:col-span-2 flex flex-col">
          <RecentIncidents incidents={recentIncidents} loading={isLoading} />
        </div>

        {/* Info Feeds */}
        <div className="flex flex-col gap-6">
          <SystemHealth healthData={health} loading={isLoading} error={isError} />
          <ThreatFeed iocs={iocsData} loading={loadingIocs} />
        </div>
      </div>
    </div>
  );
}
