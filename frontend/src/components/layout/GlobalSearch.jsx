import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { 
  HiOutlineSearch, 
  HiOutlineShieldCheck, 
  HiOutlineTerminal, 
  HiOutlineUser, 
  HiOutlineCog,
  HiOutlineLogout
} from 'react-icons/hi';
import { 
  RiDashboardLine, 
  RiAlertLine, 
  RiUploadCloud2Line, 
  RiGitRepositoryPrivateLine, 
  RiRadarLine,
  RiUserSettingsLine,
  RiHistoryLine
} from 'react-icons/ri';
import { ROUTES } from '../../constants/routes';
import { useAuth } from '../../context/AuthContext';

export default function GlobalSearch({ isOpen, onClose }) {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [query, setQuery] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery('');
    }
  }, [isOpen]);

  const commandItems = [
    { label: 'Security Dashboard', path: ROUTES.DASHBOARD, icon: RiDashboardLine, category: 'Navigation' },
    { label: 'Incident Center', path: ROUTES.INCIDENTS, icon: RiAlertLine, category: 'Navigation' },
    { label: 'Upload Cloud Logs', path: ROUTES.UPLOAD_LOGS, icon: RiUploadCloud2Line, category: 'Navigation' },
    { label: 'IOC Watchlist Registry', path: ROUTES.IOC_MANAGEMENT, icon: RiGitRepositoryPrivateLine, category: 'Navigation' },
    { label: 'Threat Intel Center', path: ROUTES.THREAT_INTEL, icon: RiRadarLine, category: 'Navigation' },
    { label: 'User Directory', path: ROUTES.USERS, icon: RiUserSettingsLine, category: 'Administration' },
    { label: 'Audit Logs', path: ROUTES.AUDIT_LOGS, icon: RiHistoryLine, category: 'Administration' },
    { label: 'Security Profile Settings', path: ROUTES.PROFILE, icon: HiOutlineUser, category: 'Configuration' },
    { label: 'System Configuration', path: ROUTES.SETTINGS, icon: HiOutlineCog, category: 'Configuration' },
    { label: 'Logout Session', action: () => logout(), icon: HiOutlineLogout, category: 'Session', danger: true },
  ];

  const filtered = commandItems.filter(item => 
    item.label.toLowerCase().includes(query.toLowerCase()) ||
    item.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (item) => {
    if (item.action) {
      item.action();
    } else if (item.path) {
      navigate(item.path);
    }
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
          {/* Backdrop overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-background/70 backdrop-blur-sm"
          />

          {/* Palette panel */}
          <motion.div
            initial={{ opacity: 0, scale: 0.97, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: -8 }}
            transition={{ duration: 0.15 }}
            className="relative w-full max-w-lg bg-surface border border-border-color rounded-xl overflow-hidden shadow-2xl p-0 mx-4 select-none"
          >
            <div className="flex items-center gap-3 px-4 py-3 border-b border-border-color">
              <HiOutlineSearch className="w-5 h-5 text-text-muted shrink-0" />
              <input
                ref={inputRef}
                type="text"
                placeholder="Search command menu..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full bg-transparent text-sm text-text-primary placeholder-text-muted outline-none border-none py-0.5"
              />
              <span className="text-[10px] bg-background border border-border-color text-text-muted rounded px-1.5 py-0.5">
                ESC
              </span>
            </div>

            <div className="max-h-80 overflow-y-auto p-2 flex flex-col gap-1.5">
              {filtered.length === 0 ? (
                <div className="py-8 text-center text-xs text-text-muted">
                  No matching workspace actions found
                </div>
              ) : (
                filtered.map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSelect(item)}
                      className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-left transition-colors cursor-pointer outline-none focus:bg-background/80 hover:bg-background/40 ${
                        item.danger ? 'text-red hover:bg-red/5' : 'text-text-primary'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-1.5 rounded-md ${item.danger ? 'bg-red/10' : 'bg-background border border-border-color/40 text-text-muted'}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <span className="text-xs font-semibold">{item.label}</span>
                      </div>
                      <span className="text-[9px] uppercase font-bold tracking-wider text-text-muted opacity-60">
                        {item.category}
                      </span>
                    </button>
                  );
                })
              )}
            </div>

            <div className="flex items-center justify-between px-4 py-2 bg-background/50 border-t border-border-color text-[10px] text-text-muted">
              <span>Use keyboard shortcuts for speed</span>
              <span>⌘K / Ctrl+K</span>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
