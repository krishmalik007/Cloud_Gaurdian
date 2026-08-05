import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { iocService } from '../services/iocService';

export const useIOCs = () => {
  return useQuery({
    queryKey: ['iocs', 'list'],
    queryFn: iocService.getIOCs,
  });
};

export const useCreateIOC = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: iocService.createIOC,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['iocs'] });
    },
  });
};

export const useUpdateIOC = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ iocId, updates }) => iocService.updateIOC(iocId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['iocs'] });
    },
  });
};

export const useDeleteIOC = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: iocService.deleteIOC,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['iocs'] });
    },
  });
};
