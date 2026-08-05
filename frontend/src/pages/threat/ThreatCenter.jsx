import React, { useState, useEffect } from 'react';
import { useThreatCheck } from '../../hooks/useThreat';
import { PageHeader } from '../../components/layout/PageHeader';

// Components
import ThreatSearchTabs from '../../components/threat/ThreatSearchTabs';
import ThreatSearch from '../../components/threat/ThreatSearch';
import ThreatResultCard from '../../components/threat/ThreatResultCard';
import ThreatEmptyState from '../../components/threat/ThreatEmptyState';
import ThreatLoading from '../../components/threat/ThreatLoading';
import ThreatError from '../../components/threat/ThreatError';
import ThreatHistory from '../../components/threat/ThreatHistory';

export default function ThreatCenter() {
  const [activeTab, setActiveTab] = useState('IP');
  const [searchValue, setSearchValue] = useState('');
  const [history, setHistory] = useState([]);

  const { data: result, isLoading, isError, error, refetch } = useThreatCheck(activeTab, searchValue);

  // Append successful lookups to session history
  useEffect(() => {
    if (result && searchValue) {
      const exists = history.some(
        (item) => item.type === activeTab && item.value.toLowerCase() === searchValue.toLowerCase()
      );
      if (!exists) {
        setHistory((prev) => [
          {
            type: activeTab,
            value: searchValue,
            malicious: result.malicious,
          },
          ...prev,
        ]);
      }
    }
  }, [result, searchValue, activeTab]);

  const handleSearch = (val) => {
    setSearchValue(val);
  };

  const handleHistoryClick = (type, val) => {
    setActiveTab(type);
    setSearchValue(val);
  };

  const handleTabChange = (newTab) => {
    setActiveTab(newTab);
    setSearchValue(''); // Clear search on tab switch
  };

  return (
    <div className="flex flex-col gap-6 w-full animate-fade-in text-left">
      <PageHeader
        title="Threat Intelligence Center"
        subtitle="Search global databases and locally correlated watchlist tables for malicious indicators."
      />

      {/* Main Grid: left search pane, right history pane */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 w-full">
        {/* Left Side: Search & Result panels */}
        <div className="xl:col-span-3 flex flex-col gap-4">
          <div className="p-5 border border-border-color bg-surface/50 rounded-xl flex flex-col gap-4">
            <ThreatSearchTabs activeTab={activeTab} onTabChange={handleTabChange} />
            <ThreatSearch onSearch={handleSearch} activeTab={activeTab} loading={isLoading} />
          </div>

          {/* Results Area */}
          {isLoading ? (
            <ThreatLoading />
          ) : isError ? (
            <ThreatError error={error} onRetry={refetch} />
          ) : result && searchValue ? (
            <ThreatResultCard result={result} />
          ) : (
            <ThreatEmptyState />
          )}
        </div>

        {/* Right Side: Session History Card */}
        <div className="xl:col-span-1">
          <ThreatHistory history={history} onHistoryClick={handleHistoryClick} />
        </div>
      </div>
    </div>
  );
}
