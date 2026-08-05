import { useQuery } from '@tanstack/react-query';
import { threatService } from '../services/threatService';

export const useThreatCheck = (type, value) => {
  const normType = String(type).toUpperCase();
  const activeValue = String(value).trim();

  return useQuery({
    queryKey: ['threat', 'check', normType, activeValue],
    queryFn: () => {
      if (normType === 'IP') return threatService.checkIP(activeValue);
      if (normType === 'DOMAIN') return threatService.checkDomain(activeValue);
      if (normType === 'USERNAME') return threatService.checkUser(activeValue);
      throw new Error(`Unsupported threat indicator type: ${type}`);
    },
    enabled: !!activeValue && ['IP', 'DOMAIN', 'USERNAME'].includes(normType),
    retry: false,
  });
};
