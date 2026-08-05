import { useQuery } from '@tanstack/react-query';
import { auditService } from '../services/auditService';

export const useAuditLogs = () => {
  return useQuery({
    queryKey: ['audit', 'list'],
    queryFn: auditService.getAuditLogs,
    keepPreviousData: true,
  });
};

export const useAuditDetail = (auditId) => {
  return useQuery({
    queryKey: ['audit', 'detail', auditId],
    queryFn: () => auditService.getAuditDetail(auditId),
    enabled: !!auditId,
  });
};
