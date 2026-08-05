import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Contexts
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';

// Layouts
import { DashboardLayout } from './layouts/DashboardLayout';
import { AuthLayout } from './layouts/AuthLayout';

// Protection
import { ProtectedRoute } from './components/ProtectedRoute';
import ErrorBoundary from './components/ui/ErrorBoundary';

// Constants
import { ROUTES } from './constants/routes';
import { ROLES } from './constants/roles';

// Lazy Loaded Pages for Performance Code Splitting
const Login = React.lazy(() => import('./pages/auth/Login'));
const Register = React.lazy(() => import('./pages/auth/Register'));
const Dashboard = React.lazy(() => import('./pages/dashboard/Dashboard'));
const Incidents = React.lazy(() => import('./pages/incidents/IncidentPage'));
const IncidentDetails = React.lazy(() => import('./pages/incidents/IncidentDetails'));
const UploadLogs = React.lazy(() => import('./pages/logs/UploadLogs'));
const IOCManagement = React.lazy(() => import('./pages/ioc/IOCManagement'));
const ThreatLookup = React.lazy(() => import('./pages/threat/ThreatCenter'));
const Users = React.lazy(() => import('./pages/users/Users'));
const AuditLogs = React.lazy(() => import('./pages/audit/AuditLogsPage'));
const Profile = React.lazy(() => import('./pages/profile/Profile'));
const Settings = React.lazy(() => import('./pages/settings/Settings'));

// Error Pages
const Error401 = React.lazy(() => import('./pages/error/Error401'));
const Error403 = React.lazy(() => import('./pages/error/Error403'));
const Error404 = React.lazy(() => import('./pages/error/Error404'));
const Error500 = React.lazy(() => import('./pages/error/Error500'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <React.Suspense fallback={
              <div className="flex flex-col gap-6 p-8 w-full animate-pulse select-none max-w-7xl mx-auto mt-6">
                <div className="h-8 bg-surface border border-border-color rounded-lg w-1/4" />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="h-28 bg-surface/50 border border-border-color/50 rounded-xl" />
                  <div className="h-28 bg-surface/50 border border-border-color/50 rounded-xl" />
                  <div className="h-28 bg-surface/50 border border-border-color/50 rounded-xl" />
                </div>
                <div className="h-80 bg-surface/30 border border-border-color/30 rounded-xl" />
              </div>
            }>
              <Routes>
                {/* Authentication Routes */}
                <Route element={<AuthLayout />}>
                <Route path={ROUTES.LOGIN} element={<Login />} />
                <Route path={ROUTES.REGISTER} element={<Register />} />
              </Route>

              {/* Protected Dashboard Routes */}
              <Route element={<DashboardLayout />}>
                <Route
                  path={ROUTES.DASHBOARD}
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.INCIDENTS}
                  element={
                    <ProtectedRoute>
                      <Incidents />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.INCIDENT_DETAILS}
                  element={
                    <ProtectedRoute>
                      <IncidentDetails />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.UPLOAD_LOGS}
                  element={
                    <ProtectedRoute>
                      <UploadLogs />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.IOC_MANAGEMENT}
                  element={
                    <ProtectedRoute>
                      <IOCManagement />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.THREAT_INTEL}
                  element={
                    <ProtectedRoute>
                      <ThreatLookup />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.PROFILE}
                  element={
                    <ProtectedRoute>
                      <Profile />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.SETTINGS}
                  element={
                    <ProtectedRoute>
                      <Settings />
                    </ProtectedRoute>
                  }
                />

                {/* Admin Only Routes */}
                <Route
                  path={ROUTES.USERS}
                  element={
                    <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                      <Users />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.AUDIT_LOGS}
                  element={
                    <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                      <AuditLogs />
                    </ProtectedRoute>
                  }
                />
              </Route>

              {/* Error Routes */}
              <Route path={ROUTES.UNAUTHORIZED} element={<Error401 />} />
              <Route path={ROUTES.FORBIDDEN} element={<Error403 />} />
              <Route path={ROUTES.SERVER_ERROR} element={<Error500 />} />
              <Route path={ROUTES.NOT_FOUND} element={<Error404 />} />
              <Route path="*" element={<Navigate to={ROUTES.NOT_FOUND} replace />} />
            </Routes>
            </React.Suspense>
          </Router>
          
          <ToastContainer
            position="top-right"
            autoClose={4000}
            hideProgressBar
            newestOnTop
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="dark"
            toastClassName="bg-sidebar border border-border-color text-text-primary rounded-xl"
          />
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
    </ErrorBoundary>
  );
}
