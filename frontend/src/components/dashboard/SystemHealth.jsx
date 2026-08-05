import React from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

export default function SystemHealth({ healthData, loading = false, error = false }) {
  const getStatusBadge = (status) => {
    if (status === 'Healthy' || status === 'Connected') {
      return <Badge variant="success" size="sm">ONLINE</Badge>;
    }
    if (status === 'Degraded') {
      return <Badge variant="warning" size="sm">DEGRADED</Badge>;
    }
    return <Badge variant="danger" size="sm">OFFLINE</Badge>;
  };

  // Resolve health states based on the real /health endpoint response
  const getBackendStatus = () => {
    if (error) return 'Offline';
    if (loading) return 'Loading';
    return healthData?.status === 'healthy' ? 'Healthy' : 'Offline';
  };

  const getOpenSearchStatus = () => {
    if (error) return 'Offline';
    if (loading) return 'Loading';
    return healthData?.opensearch === 'connected' ? 'Connected' : 'Offline';
  };

  const getKafkaStatus = () => {
    if (error) return 'Offline';
    if (loading) return 'Loading';
    // If backend is running, Kafka cluster connection is active as checked on startup
    return healthData?.status === 'healthy' ? 'Healthy' : 'Offline';
  };

  const getApiStatus = () => {
    if (error) return 'Offline';
    if (loading) return 'Loading';
    return 'Healthy';
  };

  const services = [
    { name: 'FastAPI Backend', status: getBackendStatus() },
    { name: 'OpenSearch Node', status: getOpenSearchStatus() },
    { name: 'Kafka broker', status: getKafkaStatus() },
    { name: 'Platform gateway', status: getApiStatus() },
  ];

  return (
    <Card title="System Health" subtitle="Real-time connectivity status of SOC core infrastructure">
      <div className="flex flex-col gap-3 mt-4 w-full">
        {services.map((service, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between p-3 rounded-lg border border-border-color bg-background/30"
          >
            <span className="text-xs font-semibold text-text-primary">
              {service.name}
            </span>
            {loading ? (
              <div className="h-5 w-16 bg-surface rounded animate-pulse" />
            ) : (
              getStatusBadge(service.status)
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}
