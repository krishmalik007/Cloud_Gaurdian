import React from 'react';

export const Footer = () => {
  return (
    <footer className="py-4 px-6 border-t border-border-color/50 text-center text-[10px] text-text-muted select-none">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
        <span>&copy; {new Date().getFullYear()} CloudGuardian Enterprise. All rights reserved.</span>
        <div className="flex gap-4">
          <a href="#" className="hover:text-text-secondary transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-text-secondary transition-colors">Terms of Service</a>
          <a href="#" className="hover:text-text-secondary transition-colors">Security Advisories</a>
        </div>
      </div>
    </footer>
  );
};
