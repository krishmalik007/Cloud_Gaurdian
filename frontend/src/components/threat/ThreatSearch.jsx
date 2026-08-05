import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { HiOutlineSearch, HiOutlineX } from 'react-icons/hi';

export default function ThreatSearch({ onSearch, activeTab, loading }) {
  const [value, setValue] = useState('');

  const getPlaceholder = () => {
    if (activeTab === 'IP') return 'Enter target IPv4 (e.g. 185.220.101.4)...';
    if (activeTab === 'DOMAIN') return 'Enter target domain (e.g. malicious-site.com)...';
    return 'Enter analyst username (e.g. compromised_user)...';
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (value.trim()) {
      onSearch(value.trim());
    }
  };

  const handleClear = () => {
    setValue('');
    onSearch('');
  };

  return (
    <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row items-center gap-3 w-full">
      <div className="flex-1 w-full">
        <Input
          placeholder={getPlaceholder()}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          icon={HiOutlineSearch}
          containerClassName="!gap-0"
          className="!py-2"
          rightElement={
            value ? (
              <button
                type="button"
                onClick={handleClear}
                className="text-text-muted hover:text-text-primary transition-colors cursor-pointer"
              >
                <HiOutlineX className="w-4 h-4" />
              </button>
            ) : null
          }
        />
      </div>

      <div className="flex items-center gap-3 w-full sm:w-auto">
        <Button
          type="submit"
          variant="primary"
          size="md"
          className="w-full sm:w-auto min-w-[100px]"
          isLoading={loading}
          disabled={!value.trim()}
        >
          Investigate
        </Button>
      </div>
    </form>
  );
}
