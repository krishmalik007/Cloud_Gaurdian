import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { HiOutlineMail, HiOutlineLockClosed, HiOutlineEye, HiOutlineEyeOff } from 'react-icons/hi';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../constants/routes';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';

const loginSchema = zod.object({
  email: zod.string().min(1, 'Email is required').email('Invalid email address'),
  password: zod.string().min(6, 'Password must be at least 6 characters'),
});

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const from = location.state?.from?.pathname || ROUTES.DASHBOARD;

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      await login(data.email, data.password);
      toast.success('Authentication successful! Welcome to CloudGuardian.');
      navigate(from, { replace: true });
    } catch (error) {
      const errMsg = error.response?.data?.detail || 'Invalid email or password.';
      toast.error(`Access Denied: ${errMsg}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1.5 text-center lg:text-left select-none">
        <h2 className="text-xl font-bold text-text-primary">Sign in to CloudGuardian</h2>
        <p className="text-xs text-text-secondary font-medium">
          Enter your security credentials to access the SOC telemetry.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        {/* Email Input */}
        <Input
          label="Security Email"
          type="email"
          placeholder="analyst@cloudguardian.com"
          icon={HiOutlineMail}
          error={errors.email}
          {...register('email')}
        />

        {/* Password Input */}
        <Input
          label="Credentials Password"
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

        {/* Action Button */}
        <Button
          type="submit"
          variant="primary"
          isLoading={isSubmitting}
          className="w-full mt-2"
        >
          Authenticate Analyst
        </Button>
      </form>

      <div className="text-center text-xs text-text-secondary select-none">
        New to the team?{' '}
        <Link to={ROUTES.REGISTER} className="text-primary-blue hover:underline font-semibold">
          Register Security Account
        </Link>
      </div>
    </div>
  );
}
