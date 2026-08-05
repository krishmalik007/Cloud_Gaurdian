import React from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { HiOutlineUserAdd } from 'react-icons/hi';

export default function RoleUpdateDialog({ isOpen, onClose, onConfirm, username, targetRole, isUpdating }) {
  const footer = (
    <>
      <Button variant="outline" size="sm" onClick={onClose} disabled={isUpdating}>
        Cancel
      </Button>
      <Button variant="primary" size="sm" onClick={onConfirm} isLoading={isUpdating}>
        Confirm Role Promotion
      </Button>
    </>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Modify Personnel Authorization"
      footer={footer}
      closeOnOverlayClick={!isUpdating}
    >
      <div className="flex gap-4">
        <div className="p-2.5 rounded-lg bg-primary-blue/15 text-primary-blue h-max">
          <HiOutlineUserAdd className="w-6 h-6 animate-pulse" />
        </div>
        <div className="flex flex-col gap-1.5 text-left select-none">
          <p className="text-sm font-semibold text-text-primary">
            Confirm role reassignment for user:
          </p>
          <span className="font-mono text-xs text-text-muted bg-background/50 border border-border-color rounded px-2.5 py-1.5 w-max">
            {username}
          </span>
          <p className="text-xs text-text-secondary leading-relaxed">
            Reassigning this user to **{targetRole === 'ADMIN' ? 'Administrator' : 'Security Analyst'}** will update their platform routing privileges.
          </p>
        </div>
      </div>
    </Modal>
  );
}
