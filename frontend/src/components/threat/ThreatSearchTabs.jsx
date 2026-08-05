import React from 'react';
import { HiOutlineDatabase, HiOutlineGlobe, HiOutlineUser } from 'react-icons/hi';

export default function ThreatSearchTabs({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'IP', label: 'IP Address', icon: HiOutlineDatabase },
    { id: 'DOMAIN', label: 'Domain Name', icon: HiOutlineGlobe },
    { id: 'USERNAME', label: 'User Identity', icon: HiOutlineUser },
  ];

  return (
    <div className="flex border-b border-border-color/50 mb-6 select-none">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex items-center gap-2 px-5 py-3 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
              isActive
                ? 'border-primary-blue text-primary-blue'
                : 'border-transparent text-text-secondary hover:text-text-primary'
            }`}
          >
            <Icon className="w-4 h-4" />
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
