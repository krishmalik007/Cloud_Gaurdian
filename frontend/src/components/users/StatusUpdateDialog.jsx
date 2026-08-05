import React from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { HiOutlineLockClosed, HiOutlineLockOpen } from 'react-icons/hi';

export default function StatusUpdateDialog({ isOpen, onClose, onConfirm, username, targetEnabled, isUpdating }) {
  const footer = (
    <>
      <Button variant="outline" size="sm" onClick={onClose} disabled={isUpdating}>
        Cancel
      </Button>
      <Button
        variant={targetEnabled ? 'primary' : 'danger'}
        size="sm"
        onClick={onConfirm}
        isLoading={isUpdating}
      >
        {targetEnabled ? 'Activate Account' : 'Deactivate Account'}
      </Button>
    </>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={targetEnabled ? 'Enable Account Access' : 'Disable Account Access'}
      footer={footer}
      closeOnOverlayClick={!isUpdating}
    >
      <div className="flex gap-4">
        <div className={`p-2.5 rounded-lg h-max ${targetEnabled ? 'bg-green/10 text-green' : 'bg-red/10 text-red'}`}>
          {targetEnabled ? <HiOutlineLockOpen className="w-6 h-6" /> : <HiOutlineLockClosed className="w-6 h-6 animate-pulse" />}
        </div>
        <div className="flex flex-col gap-1.5 text-left select-none">
          <p className="text-sm font-semibold text-text-primary">
            Confirm user status update:
          </p>
          <span className="font-mono text-xs text-text-muted bg-background/50 border border-border-color rounded px-2.5 py-1.5 w-max">
            {username}
          </span>
          <p className="text-xs text-text-secondary leading-relaxed">
            {targetEnabled
              ? 'This account will be activated and granted system access credentials.'
              : 'This account will be locked out and will not be able to log in.'}
          </p>
        </div>
      </div>
    </Modal>
  );
}
