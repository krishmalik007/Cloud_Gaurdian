import React from 'react';
import { HiMenuAlt1, HiOutlineSearch, HiOutlineUser, HiOutlineLockClosed } from 'react-icons/hi';
import { Breadcrumbs } from '../ui/Breadcrumbs';
import { Dropdown } from '../ui/Dropdown';
import { Avatar } from '../ui/Avatar';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../constants/routes';
import { useNavigate } from 'react-router-dom';
import NotificationCenter from './NotificationCenter';

export const Navbar = ({ isCollapsed, setIsMobileOpen, onSearchClick }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const profileMenuItems = [
    {
      label: 'Security Profile',
      icon: HiOutlineUser,
      onClick: () => navigate(ROUTES.PROFILE),
    },
    {
      label: 'System Settings',
      icon: HiOutlineUser,
      onClick: () => navigate(ROUTES.SETTINGS),
    },
    { divider: true },
    {
      label: 'Sign Out',
      icon: HiOutlineLockClosed,
      danger: true,
      onClick: () => logout(),
    },
  ];

  return (
    <header className="sticky top-0 right-0 z-30 flex items-center justify-between h-16 px-6 bg-background/80 backdrop-blur-md border-b border-border-color">
      {/* Left side: Hamburger (mobile) + Breadcrumbs */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => setIsMobileOpen(true)}
          className="lg:hidden p-1.5 rounded-lg border border-border-color hover:bg-surface text-text-muted hover:text-text-primary transition-colors cursor-pointer"
        >
          <HiMenuAlt1 className="w-5 h-5" />
        </button>
        <Breadcrumbs />
      </div>

      {/* Right side: Search, Notifications, Profile */}
      <div className="flex items-center gap-4">
        {/* Quick Search */}
        <button
          onClick={onSearchClick}
          className="relative hidden md:flex items-center bg-surface/50 border border-border-color rounded-lg py-1.5 pl-9 pr-4 text-xs text-text-muted w-64 text-left hover:border-primary-blue/50 transition-colors cursor-pointer focus:outline-none focus:ring-1 focus:ring-primary-blue/30 select-none"
        >
          <HiOutlineSearch className="absolute left-3 w-4 h-4 text-text-muted pointer-events-none" />
          <span>Search command menu...</span>
          <span className="absolute right-2 text-[9px] bg-background border border-border-color px-1.5 py-0.5 rounded text-text-muted">
            Ctrl K
          </span>
        </button>

        {/* Notifications */}
        <NotificationCenter />

        {/* User profile dropdown */}
        <Dropdown
          trigger={
            <button className="flex items-center gap-2 p-1 hover:bg-surface/50 rounded-lg transition-colors cursor-pointer border border-transparent hover:border-border-color select-none">
              <Avatar username={user?.username || 'Analyst'} size="sm" status="online" />
              <div className="hidden sm:flex flex-col text-left">
                <span className="text-xs font-semibold text-text-primary leading-tight">
                  {user?.username || 'Cloud Analyst'}
                </span>
                <span className="text-[10px] text-text-muted font-medium uppercase leading-none">
                  {user?.role || 'ANALYST'}
                </span>
              </div>
            </button>
          }
          items={profileMenuItems}
          align="right"
        />
      </div>
    </header>
  );
};
