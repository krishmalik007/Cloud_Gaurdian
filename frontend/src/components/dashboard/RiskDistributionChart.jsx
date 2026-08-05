import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Card } from '../ui/Card';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function RiskDistributionChart({ data = [], loading = false }) {
  const parseChartData = () => {
    const riskLevels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    const riskCounts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };

    data.forEach((item) => {
      const level = String(item.risk_level).toUpperCase();
      if (riskCounts[level] !== undefined) {
        riskCounts[level] = item.count;
      }
    });

    const colors = {
      CRITICAL: '#EF4444', // Red
      HIGH: '#F59E0B',     // Orange
      MEDIUM: '#3B82F6',   // Blue
      LOW: '#22C55E',      // Green
    };

    return {
      labels: riskLevels,
      datasets: [
        {
          data: riskLevels.map((l) => riskCounts[l]),
          backgroundColor: riskLevels.map((l) => colors[l]),
          borderRadius: 6,
          barThickness: 28,
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
    <Card title="Risk Distribution" subtitle="Number of incidents classified by severity level">
      <div className="h-64 relative mt-4">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-surface animate-pulse" />
        ) : data.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-text-muted">
            No risk distribution metrics available. Ingest logs to begin.
          </div>
        ) : (
          <Bar data={chartData} options={options} />
        )}
      </div>
    </Card>
  );
}
