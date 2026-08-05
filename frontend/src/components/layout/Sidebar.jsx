import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HiOutlineShieldCheck, 
  HiOutlineChevronLeft, 
  HiOutlineChevronRight,
  HiOutlineOfficeBuilding,
  HiOutlineLockClosed,
  HiOutlineLogout
} from 'react-icons/hi';
import { 
  RiDashboardLine, 
  RiAlertLine, 
  RiUploadCloud2Line,
  RiGitRepositoryPrivateLine,
  RiRadarLine,
  RiUserSettingsLine,
  RiHistoryLine,
  RiUserSettingsFill,
  RiSettings4Line
} from 'react-icons/ri';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../constants/routes';
import { ROLES } from '../../constants/roles';

export const Sidebar = ({ isCollapsed, setIsCollapsed, isMobileOpen, setIsMobileOpen }) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const menuGroups = [
    {
      title: 'Overview',
      items: [
        { label: 'Dashboard', path: ROUTES.DASHBOARD, icon: RiDashboardLine },
      ]
    },
    {
      title: 'Security Operations',
      items: [
        { label: 'Incidents', path: ROUTES.INCIDENTS, icon: RiAlertLine },
        { label: 'Upload Logs', path: ROUTES.UPLOAD_LOGS, icon: RiUploadCloud2Line },
      ]
    },
    {
      title: 'Threat Intelligence',
      items: [
        { label: 'IOC Management', path: ROUTES.IOC_MANAGEMENT, icon: RiGitRepositoryPrivateLine },
        { label: 'Threat Lookup', path: ROUTES.THREAT_INTEL, icon: RiRadarLine },
      ]
    },
    {
      title: 'Administration',
      roles: [ROLES.ADMIN],
      items: [
        { label: 'Users', path: ROUTES.USERS, icon: RiUserSettingsLine },
        { label: 'Audit Logs', path: ROUTES.AUDIT_LOGS, icon: RiHistoryLine },
      ]
    },
    {
      title: 'System',
      items: [
        { label: 'Profile', path: ROUTES.PROFILE, icon: RiUserSettingsFill },
        { label: 'Settings', path: ROUTES.SETTINGS, icon: RiSettings4Line },
      ]
    }
  ];

  const handleLinkClick = () => {
    if (isMobileOpen) {
      setIsMobileOpen(false);
    }
  };

  const isActive = (path) => {
    if (path === ROUTES.DASHBOARD) {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <>
      {/* Mobile Backdrop overlay */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-45 flex flex-col bg-sidebar border-r border-border-color transition-all duration-300 ${
          isCollapsed ? 'w-16' : 'w-64'
        } ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Sidebar Header Brand logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-border-color bg-background/20 select-none">
          <Link 
            to={ROUTES.DASHBOARD} 
            onClick={handleLinkClick}
            className="flex items-center gap-2.5 overflow-hidden"
          >
            <HiOutlineShieldCheck className="w-7 h-7 text-primary-blue flex-shrink-0" />
            {!isCollapsed && (
              <span className="font-bold text-base tracking-tight text-text-primary whitespace-nowrap">
                Cloud<span className="text-primary-blue">Guardian</span>
              </span>
            )}
          </Link>
          
          {/* Collapse button - desktop only */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden lg:flex items-center justify-center w-6 h-6 border border-border-color rounded bg-surface hover:bg-background text-text-muted hover:text-text-primary transition-colors cursor-pointer"
          >
            {isCollapsed ? <HiOutlineChevronRight className="w-4.5 h-4.5" /> : <HiOutlineChevronLeft className="w-4.5 h-4.5" />}
          </button>
        </div>

        {/* Scrollable Navigation items */}
        <div className="flex-1 overflow-y-auto px-3 py-4 flex flex-col gap-5">
          {menuGroups.map((group, groupIdx) => {
            // Check if group is permitted for current user's role
            if (group.roles && (!user || !group.roles.includes(user.role))) {
              return null;
            }

            return (
              <div key={groupIdx} className="flex flex-col gap-1">
                {/* Group Title */}
                {!isCollapsed && (
                  <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider px-3 mb-1 select-none">
                    {group.title}
                  </span>
                )}
                {isCollapsed && (
                  <div className="h-px bg-border-color my-1 mx-1" />
                )}

                {/* Group items */}
                {group.items.map((item, itemIdx) => {
                  const Icon = item.icon;
                  const active = isActive(item.path);
                  
                  return (
                    <Link
                      key={itemIdx}
                      to={item.path}
                      onClick={handleLinkClick}
                      className={`flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-lg transition-all select-none ${
                        active
                          ? 'bg-primary-blue/10 text-primary-blue font-semibold border border-primary-blue/20'
                          : 'text-text-secondary hover:bg-surface/50 hover:text-text-primary border border-transparent'
                      }`}
                    >
                      <Icon className={`w-4.5 h-4.5 flex-shrink-0 ${active ? 'text-primary-blue' : 'text-text-muted'}`} />
                      {!isCollapsed && <span className="whitespace-nowrap">{item.label}</span>}
                    </Link>
                  );
                })}
              </div>
            );
          })}
        </div>

        {/* Bottom Actions footer */}
        <div className="p-3 border-t border-border-color bg-background/10">
          <button
            onClick={() => {
              logout();
              handleLinkClick();
            }}
            className="flex items-center gap-3 w-full px-3 py-2.5 text-xs font-semibold rounded-lg text-red hover:bg-red/10 transition-colors cursor-pointer"
          >
            <HiOutlineLogout className="w-4.5 h-4.5 flex-shrink-0" />
            {!isCollapsed && <span>Sign Out</span>}
          </button>
        </div>
      </aside>
    </>
  );
};
