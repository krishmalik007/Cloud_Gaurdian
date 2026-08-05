# CloudGuardian Frontend Task List (Phase 1, 2, 3, 4, 5 & 6)

## Phase 1: Foundation, Routing & Reusable Design System (Complete)
- [x] Initialize Vite project in `frontend/` directory
- [x] Install core dependencies
- [x] Configure Tailwind CSS with semantic dark-mode colors
- [x] Set up environment files
- [x] Create constants (`roles.js`, `routes.js`, `severity.js`, `status.js`)
- [x] Implement Reusable Design System components
- [x] Implement Contexts
- [x] Create Layout and Layout Components
- [x] Implement Axios Client and protected routing hooks
- [x] Set up basic Error Pages (401, 403, 404, 500)
- [x] Build Login and Register Pages
- [x] Verify Phase 1 builds successfully without errors

## Phase 2: SOC Dashboard, Analytics, & Charts (Complete)
- [x] Create dashboard API service (`dashboardService.js`)
- [x] Setup custom TanStack Query hooks (`useDashboard.js`)
- [x] Build dashboard widgets in `src/components/dashboard/`
- [x] Assemble master view in `src/pages/dashboard/Dashboard.jsx`
- [x] Verify compilation and responsiveness of Phase 2 build

## Phase 3: Enterprise Incident Center & Operations (Complete)
- [x] Create incident API service (`incidentService.js`)
- [x] Create custom TanStack Query hooks (`useIncidents.js`)
- [x] Build incident center components in `src/components/incidents/`
- [x] Assemble master page in `src/pages/incidents/IncidentPage.jsx`
- [x] Ingest Telemetry Logs page built at `src/pages/logs/UploadLogs.jsx` (providing AWS/Azure templates and live correlation results)
- [x] Verify build compilation and responsiveness of Phase 3 build

## Phase 4: Enterprise IOC Management (Complete)
- [x] Create IOC API service (`iocService.js`)
- [x] Create custom TanStack Query hooks (`useIOC.js`)
- [x] Build IOC management components in `src/components/ioc/`
- [x] Assemble master page in `src/pages/ioc/IOCManagement.jsx`
- [x] Verify build compilation and responsiveness of Phase 4 build

## Phase 5: Enterprise Threat Intelligence Center (Complete)
- [x] Create threat API service (`threatService.js` for IP, domain, and user checks)
- [x] Create custom TanStack Query hook (`useThreat.js` to handle queries by indicator type)
- [x] Build threat lookup components in `src/components/threat/`
- [x] Assemble master page in `src/pages/threat/ThreatCenter.jsx`
- [x] Verify build compilation and responsiveness of Phase 5 build

## Phase 6: Enterprise Audit Logs Center (Complete)
- [x] Create audit API service (`auditService.js` to call GET `/audit/` and `/audit/{audit_id}`)
- [x] Create custom TanStack Query hooks (`useAudit.js` for lists and details)
- [x] Build audit center components in `src/components/audit/`:
  - [x] `AuditStats` (Total, Success, Failed, and Unique User counters)
  - [x] `AuditToolbar` (combines search bar, action selects, status filters, and refresh button)
  - [x] `AuditTable` (data grid with custom cell badges and timestamps)
  - [x] `AuditRow` (styled table row hover components)
  - [x] `AuditDrawer` (slide-out event log viewer showing raw JSON, users, and resources)
  - [x] `AuditTimeline` (ingestion step indicator)
  - [x] `AuditActionBadge` & `AuditStatusBadge` (colored status and action tags)
  - [x] `AuditUserCard` (analyst profile details)
  - [x] `AuditMetadata` (triage credentials list)
  - [x] `AuditEmptyState`, `AuditLoading`, & `AuditError` (custom skeletons, descriptions, and admin-only restriction screens)
- [x] Assemble master page in `src/pages/audit/AuditLogsPage.jsx`
- [x] Verify build compilation and responsiveness of Phase 6 build
