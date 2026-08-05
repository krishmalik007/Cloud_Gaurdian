import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
import { Card } from '../ui/Card';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
);

export default function ProviderChart({ data = [], loading = false }) {
  const parseChartData = () => {
    if (!data || data.length === 0) {
      return {
        labels: ['No Data'],
        datasets: [{ data: [1], backgroundColor: ['#1E293B'] }],
      };
    }

    const labels = data.map((item) => String(item.provider).toUpperCase());
    const counts = data.map((item) => item.count);

    const colors = {
      AWS: '#F99000', // Amazon Orange
      AZURE: '#007FFF', // Azure Blue
      GCP: '#4285F4', // GCP Google Blue
    };

    const backgroundColors = labels.map((l) => colors[l] || '#7C3AED');

    return {
      labels,
      datasets: [
        {
          data: counts,
          backgroundColor: backgroundColors,
          borderWidth: 1,
          borderColor: '#1E293B',
          hoverOffset: 4,
        },
      ],
    };
  };

  const chartData = parseChartData();

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#94A3B8',
          padding: 16,
          font: {
            size: 11,
            family: 'Inter',
          },
        },
      },
      tooltip: {
        backgroundColor: '#111827',
        titleColor: '#FFFFFF',
        bodyColor: '#94A3B8',
        borderColor: 'rgba(255, 255, 255, 0.08)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
      },
    },
    cutout: '70%',
  };

  return (
    <Card title="Provider Stream" subtitle="Incident volume breakdown by cloud provider">
      <div className="h-64 relative mt-4">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-surface animate-pulse" />
        ) : data.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-text-muted">
            No cloud provider telemetry stream detected.
          </div>
        ) : (
          <Doughnut data={chartData} options={options} />
        )}
      </div>
    </Card>
  );
}
