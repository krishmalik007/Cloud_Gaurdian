import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { HiOutlineUser, HiOutlineMail, HiOutlineLockClosed, HiOutlineEye, HiOutlineEyeOff, HiOutlineShieldCheck } from 'react-icons/hi';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../constants/routes';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';

const registerSchema = zod.object({
  username: zod.string().min(3, 'Username must be at least 3 characters').max(50),
  email: zod.string().min(1, 'Email is required').email('Invalid email address'),
  password: zod.string().min(8, 'Password must be at least 8 characters'),
  role: zod.enum(['ANALYST', 'ADMIN']),
});

export default function Register() {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: '',
      email: '',
      password: '',
      role: 'ANALYST',
    },
  });

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      await registerUser(data.username, data.email, data.password, data.role);
      toast.success('Registration request sent successfully! You can now log in.');
      navigate(ROUTES.LOGIN);
    } catch (error) {
      const errMsg = error.response?.data?.detail || 'Registration failed.';
      toast.error(`Registration Error: ${errMsg}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1.5 text-center lg:text-left select-none">
        <h2 className="text-xl font-bold text-text-primary">Create Security Account</h2>
        <p className="text-xs text-text-secondary font-medium">
          Register to join the CloudGuardian Security Operations Center.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        {/* Username */}
        <Input
          label="Analyst Handle"
          type="text"
          placeholder="e.g. krish_sec"
          icon={HiOutlineUser}
          error={errors.username}
          {...register('username')}
        />

        {/* Email */}
        <Input
          label="Corporate Email"
          type="email"
          placeholder="analyst@cloudguardian.com"
          icon={HiOutlineMail}
          error={errors.email}
          {...register('email')}
        />

        {/* Password */}
        <Input
          label="Security Passphrase"
          type={showPassword ? 'text' : 'password'}
          placeholder="••••••••"
          icon={HiOutlineLockClosed}
          error={errors.password}
          rightElement={
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-text-muted hover:text-text-primary transition-colors cursor-pointer focus:outline-none"
            >
              {showPassword ? <HiOutlineEyeOff className="w-4 h-4" /> : <HiOutlineEye className="w-4 h-4" />}
            </button>
          }
          {...register('password')}
        />

        {/* Role Select */}
        <div className="flex flex-col gap-1.5 w-full">
          <label className="text-xs font-semibold text-text-secondary select-none">
            Assigned Operations Role
          </label>
          <div className="relative flex items-center w-full">
            <div className="absolute left-3 text-text-muted pointer-events-none">
              <HiOutlineShieldCheck className="w-4 h-4" />
            </div>
            <select
              className="w-full bg-background border border-border-color rounded-lg py-2 pl-9 pr-3 text-sm text-text-primary transition-all duration-200 outline-none focus:border-primary-blue focus:ring-1 focus:ring-primary-blue/30"
              {...register('role')}
            >
              <option value="ANALYST">SOC Security Analyst (Default)</option>
              <option value="ADMIN">SOC System Administrator</option>
            </select>
          </div>
          {errors.role && (
            <span className="text-xs text-red font-medium leading-none select-none">
              {errors.role.message}
            </span>
          )}
        </div>

        {/* Action Button */}
        <Button
          type="submit"
          variant="primary"
          isLoading={isSubmitting}
          className="w-full mt-2"
        >
          Request Operational Access
        </Button>
      </form>

      <div className="text-center text-xs text-text-secondary select-none">
        Already registered?{' '}
        <Link to={ROUTES.ROUTES_LOGIN || ROUTES.LOGIN} className="text-primary-blue hover:underline font-semibold">
          Sign In
        </Link>
      </div>
    </div>
  );
}
