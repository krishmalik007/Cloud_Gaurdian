import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { Drawer } from '../ui/Drawer';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { HiOutlineShieldCheck } from 'react-icons/hi';

const iocUpdateSchema = zod.object({
  severity: zod.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
  description: zod.string().optional(),
  enabled: zod.boolean(),
});

export default function EditIOCDrawer({ isOpen, onClose, onSubmit, ioc, isSubmitting }) {
  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(iocUpdateSchema),
    defaultValues: {
      severity: 'MEDIUM',
      description: '',
      enabled: true,
    },
  });

  useEffect(() => {
    if (ioc) {
      setValue('severity', ioc.severity);
      setValue('description', ioc.description || '');
      setValue('enabled', ioc.enabled);
    }
  }, [ioc, setValue]);

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
        Save Changes
      </Button>
    </>
  );

  return (
    <Drawer
      isOpen={isOpen}
      onClose={() => { reset(); onClose(); }}
      title={ioc ? `Edit Indicator: ${ioc.value}` : 'Edit Indicator'}
      size="md"
      footer={footer}
    >
      {ioc && (
        <form className="flex flex-col gap-5 text-left">
          {/* Read-only Value */}
          <div className="flex flex-col gap-1 p-3 bg-background border border-border-color rounded-lg select-all">
            <span className="text-[10px] font-bold text-text-muted uppercase">Indicator Pattern</span>
            <span className="font-mono text-sm font-semibold text-text-primary mt-1">{ioc.value}</span>
            <span className="text-[10px] text-text-muted mt-1 uppercase font-medium">Type: {ioc.type}</span>
          </div>

          {/* Severity Select */}
          <div className="flex flex-col gap-1.5 w-full">
            <label className="text-xs font-semibold text-text-secondary select-none">
              Risk Severity Level
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

          {/* Description */}
          <div className="flex flex-col gap-1.5 w-full">
            <label className="text-xs font-semibold text-text-secondary select-none">
              Context Description
            </label>
            <textarea
              rows="4"
              placeholder="Attribution details..."
              className="w-full bg-background border border-border-color rounded-lg py-2 px-3 text-sm text-text-primary placeholder-text-muted transition-all duration-200 outline-none focus:border-primary-blue focus:ring-1 focus:ring-primary-blue/30"
              {...register('description')}
            />
          </div>

          {/* Enabled Checkbox */}
          <div className="flex items-center gap-2 mt-1 select-none">
            <input
              type="checkbox"
              id="edit-ioc-enabled"
              className="rounded border-border-color bg-background text-primary-blue focus:ring-primary-blue"
              {...register('enabled')}
            />
            <label htmlFor="edit-ioc-enabled" className="text-xs font-semibold text-text-secondary">
              Keep indicator active on watchlist
            </label>
          </div>
        </form>
      )}
    </Drawer>
  );
}
