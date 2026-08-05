import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Card } from '../ui/Card';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function IncidentTrendChart({ data = [], loading = false }) {
  // Process real backend incidents data to generate a trend over time
  const parseChartData = () => {
    if (!data || data.length === 0) {
      return {
        labels: ['No Data'],
        datasets: [{ data: [0] }],
      };
    }

    // Group incidents by day (or hour if recent)
    const counts = {};
    [...data].reverse().forEach((incident) => {
      const date = new Date(incident.created_at);
      const label = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      counts[label] = (counts[label] || 0) + 1;
    });

    const labels = Object.keys(counts);
    const chartValues = Object.values(counts);

    return {
      labels,
      datasets: [
        {
          label: 'Alert Telemetry Stream',
          data: chartValues,
          fill: true,
          borderColor: '#2563EB',
          backgroundColor: 'rgba(37, 99, 235, 0.08)',
          tension: 0.4,
          pointBackgroundColor: '#2563EB',
          pointBorderColor: '#0B1220',
          pointHoverRadius: 6,
          borderWidth: 2,
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
        display: false,
      },
      tooltip: {
        backgroundColor: '#111827',
        titleColor: '#FFFFFF',
        bodyColor: '#94A3B8',
        borderColor: 'rgba(255, 255, 255, 0.08)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        displayColors: false,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#64748B',
          font: {
            size: 10,
            family: 'Inter',
          },
        },
      },
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.03)',
        },
        border: {
          dash: [5, 5],
        },
        ticks: {
          color: '#64748B',
          font: {
            size: 10,
            family: 'Inter',
          },
          precision: 0,
        },
      },
    },
  };

  return (
    <Card title="Incident Trend" subtitle="Volume of correlated security events over time">
      <div className="h-64 relative mt-4">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-surface animate-pulse" />
        ) : data.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-text-muted">
            No incident trend telemetry available. Ingest logs to begin.
          </div>
        ) : (
          <Line data={chartData} options={options} />
        )}
      </div>
    </Card>
  );
}
