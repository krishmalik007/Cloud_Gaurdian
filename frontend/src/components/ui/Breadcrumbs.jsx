import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { HiOutlineChevronRight } from 'react-icons/hi';
import { ROUTES } from '../../constants/routes';

export const Breadcrumbs = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  if (location.pathname === ROUTES.LOGIN || location.pathname === ROUTES.REGISTER) {
    return null;
  }

  // Create a mapping of path parts to human-readable names
  const routeNames = {
    admin: 'Administration',
    users: 'User Management',
    audit: 'Audit Logs',
    threat: 'Threat Intelligence',
    iocs: 'IOC Management',
    search: 'Threat Lookup',
    operations: 'Security Operations',
    upload: 'Upload Logs',
    incidents: 'Incidents',
    settings: 'Settings',
    profile: 'Profile',
    config: 'Configuration',
  };

  const getRouteLabel = (part) => {
    return routeNames[part] || part.charAt(0).toUpperCase() + part.slice(1);
  };

  return (
    <nav className="flex items-center gap-1.5 text-xs text-text-muted font-medium select-none">
      <Link
        to={ROUTES.DASHBOARD}
        className="hover:text-text-primary transition-colors"
      >
        CloudGuardian
      </Link>
      
      {pathnames.map((value, index) => {
        const last = index === pathnames.length - 1;
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;

        // If it's a dynamic route parameter like :id, style it separately
        const isParam = /^[a-fA-F0-9-]{24,36}$|^[0-9]+$/.test(value);
        const label = isParam ? `ID: ${value.slice(0, 8)}...` : getRouteLabel(value);

        return (
          <React.Fragment key={to}>
            <HiOutlineChevronRight className="w-3.5 h-3.5" />
            {last ? (
              <span className="text-text-secondary font-semibold">
                {label}
              </span>
            ) : (
              <Link
                to={to}
                className="hover:text-text-primary transition-colors"
              >
                {label}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
