import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/layout/Sidebar';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import GlobalSearch from '../components/layout/GlobalSearch';
import { useWebSocket } from '../hooks/useWebSocket';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import { RiAlertLine } from 'react-icons/ri';

export const DashboardLayout = () => {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    return localStorage.getItem('cg-sidebar-collapsed') === 'true';
  });
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const queryClient = useQueryClient();

  // Initialize global WebSocket connection for real-time updates across all pages
  useWebSocket('/ws/dashboard', (data) => {
    if (data.type === 'incident_created') {
      const incident = data.data || {};
      let threshold = 75;
      try {
        threshold = parseInt(localStorage.getItem('cg_settings_threshold') || '75', 10);
      } catch (e) {}

      if (incident.risk_score >= threshold) {
        toast.error(`CRITICAL: New Incident Detected: ${incident.title || incident.event_name || 'Unknown'}`, {
          icon: <RiAlertLine />,
          autoClose: 8000,
        });
      } else {
        toast.info(`New Incident Detected: ${incident.title || incident.event_name || 'Unknown'}`, {
          autoClose: 4000,
        });
      }
      // Globally invalidate caches to refresh both summary cards and incident lists
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
    }
  });

  // Sync collapsed state to localStorage
  useEffect(() => {
    localStorage.setItem('cg-sidebar-collapsed', isCollapsed);
  }, [isCollapsed]);

  // Global keybind listener for Ctrl+K / Cmd+K
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen bg-background text-text-primary flex">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={isCollapsed}
        setIsCollapsed={setIsCollapsed}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          isCollapsed ? 'lg:pl-16' : 'lg:pl-64'
        }`}
      >
        {/* Sticky top navigation */}
        <Navbar 
          isCollapsed={isCollapsed} 
          setIsMobileOpen={setIsMobileOpen}
          onSearchClick={() => setIsSearchOpen(true)}
        />

        {/* Content Route Outlet */}
        <main className="flex-grow p-6 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>

        {/* Footer */}
        <Footer />
      </div>

      {/* Global Command Palette */}
      <GlobalSearch isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </div>
  );
};
