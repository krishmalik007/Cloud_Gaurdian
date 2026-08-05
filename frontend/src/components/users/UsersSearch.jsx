import React, { useState, useEffect } from 'react';
import { HiOutlineSearch, HiOutlineX } from 'react-icons/hi';
import { Input } from '../ui/Input';

export default function UsersSearch({ value, onChange }) {
  const [localSearch, setLocalSearch] = useState(value);

  // Debounce search
  useEffect(() => {
    const handler = setTimeout(() => {
      onChange(localSearch);
    }, 450);

    return () => clearTimeout(handler);
  }, [localSearch]);

  return (
    <div className="w-full md:max-w-xs relative flex items-center">
      <Input
        placeholder="Search username, ID or email..."
        value={localSearch}
        onChange={(e) => setLocalSearch(e.target.value)}
        icon={HiOutlineSearch}
        containerClassName="!gap-0"
        className="!py-1.5"
        rightElement={
          localSearch ? (
            <button
              onClick={() => setLocalSearch('')}
              className="text-text-muted hover:text-text-primary transition-colors cursor-pointer"
            >
              <HiOutlineX className="w-3.5 h-3.5" />
            </button>
          ) : null
        }
      />
    </div>
  );
}
