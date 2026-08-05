import React from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { HiOutlineExclamation } from 'react-icons/hi';

export default function DeleteUserDialog({ isOpen, onClose, onConfirm, username, isDeleting }) {
  const footer = (
    <>
      <Button variant="outline" size="sm" onClick={onClose} disabled={isDeleting}>
        Cancel Action
      </Button>
      <Button variant="danger" size="sm" onClick={onConfirm} isLoading={isDeleting}>
        Delete Account Profile
      </Button>
    </>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Confirm Delete Account"
      footer={footer}
      closeOnOverlayClick={!isDeleting}
    >
      <div className="flex gap-4">
        <div className="p-2.5 rounded-lg bg-red/10 border border-red/20 text-red h-max">
          <HiOutlineExclamation className="w-6 h-6 animate-pulse" />
        </div>
        <div className="flex flex-col gap-1.5 text-left select-none">
          <p className="text-sm font-semibold text-text-primary">
            Confirm user account deletion:
          </p>
          <span className="font-mono text-xs text-text-muted bg-background/50 border border-border-color rounded px-2.5 py-1.5 w-max">
            {username}
          </span>
          <p className="text-xs text-text-secondary leading-relaxed">
            Warning: This action is irreversible. The user profile and credentials will be removed from OpenSearch.
          </p>
        </div>
      </div>
    </Modal>
  );
}
