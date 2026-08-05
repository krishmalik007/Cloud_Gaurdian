import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { HiOutlineTag, HiOutlineShieldCheck } from 'react-icons/hi';

const iocCreateSchema = zod.object({
  type: zod.enum(['IP', 'DOMAIN', 'USERNAME']),
  value: zod.string().min(1, 'Indicator pattern is required'),
  severity: zod.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
  source: zod.string().min(1, 'Source descriptor is required'),
  description: zod.string().optional(),
  enabled: zod.boolean().default(true),
});

export default function CreateIOCModal({ isOpen, onClose, onSubmit, isSubmitting }) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(iocCreateSchema),
    defaultValues: {
      type: 'IP',
      value: '',
      severity: 'MEDIUM',
      source: 'MANUAL',
      description: '',
      enabled: true,
    },
  });

  const handleFormSubmit = async (data) => {
    await onSubmit(data);
    reset();
  };

  const footer = (
    <>
      <Button variant="outline" size="sm" onClick={() => { reset(); onClose(); }} disabled={isSubmitting}>
        Cancel
      </Button>
      <Button variant="primary" size="sm" onClick={handleSubmit(handleFormSubmit)} isLoading={isSubmitting}>
        Register Indicator
      </Button>
    </>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => { reset(); onClose(); }}
      title="Create Indicator of Compromise (IOC)"
      footer={footer}
      closeOnOverlayClick={!isSubmitting}
    >
      <form className="flex flex-col gap-4 text-left">
        {/* Type Select */}
        <div className="flex flex-col gap-1.5 w-full">
          <label className="text-xs font-semibold text-text-secondary select-none">
            Indicator Type
          </label>
          <div className="relative flex items-center w-full">
            <div className="absolute left-3 text-text-muted pointer-events-none">
              <HiOutlineTag className="w-4 h-4" />
            </div>
            <select
              className="w-full bg-background border border-border-color rounded-lg py-2 pl-9 pr-3 text-sm text-text-primary outline-none focus:border-primary-blue focus:ring-1 focus:ring-primary-blue/30"
              {...register('type')}
            >
              <option value="IP">Source IP Address</option>
              <option value="DOMAIN">Malicious Domain</option>
              <option value="USERNAME">Target Username</option>
            </select>
          </div>
        </div>

        {/* Value */}
        <Input
          label="Indicator Pattern / Value"
          type="text"
          placeholder="e.g. 185.220.101.4 or suspicious-login-check"
          error={errors.value}
          {...register('value')}
        />

        {/* Severity */}
        <div className="flex flex-col gap-1.5 w-full">
          <label className="text-xs font-semibold text-text-secondary select-none">
            Risk Severity
          </label>
          <div className="relative flex items-center w-full">
            <div className="absolute left-3 text-text-muted pointer-events-none">
              <HiOutlineShieldCheck className="w-4 h-4" />
            </div>
            <select
              className="w-full bg-background border border-border-color rounded-lg py-2 pl-9 pr-3 text-sm text-text-primary outline-none focus:border-primary-blue focus:ring-1 focus:ring-primary-blue/30"
              {...register('severity')}
            >
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>

        {/* Source */}
        <Input
          label="Intelligence Feed Source"
          type="text"
          placeholder="MANUAL, ThreatConnect, AlienVault..."
          error={errors.source}
          {...register('source')}
        />

        {/* Description */}
        <div className="flex flex-col gap-1.5 w-full">
          <label className="text-xs font-semibold text-text-secondary select-none">
            Indicator Context Description
          </label>
          <textarea
            rows="3"
            placeholder="Document associated campaign details or threat actor attribution..."
            className="w-full bg-background border border-border-color rounded-lg py-2 px-3 text-sm text-text-primary placeholder-text-muted transition-all duration-200 outline-none focus:border-primary-blue focus:ring-1 focus:ring-primary-blue/30"
            {...register('description')}
          />
        </div>

        {/* Enabled Checkbox */}
        <div className="flex items-center gap-2 mt-1 select-none">
          <input
            type="checkbox"
            id="create-ioc-enabled"
            className="rounded border-border-color bg-background text-primary-blue focus:ring-primary-blue"
            {...register('enabled')}
          />
          <label htmlFor="create-ioc-enabled" className="text-xs font-semibold text-text-secondary">
            Enable correlation check immediately
          </label>
        </div>
      </form>
    </Modal>
  );
}
