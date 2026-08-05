import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services/userService';

export const useUsersList = () => {
  return useQuery({
    queryKey: ['users', 'list'],
    queryFn: userService.getUsers,
    keepPreviousData: true,
  });
};

export const useUserDetail = (userId) => {
  return useQuery({
    queryKey: ['users', 'detail', userId],
    queryFn: () => userService.getUser(userId),
    enabled: !!userId,
  });
};

export const useUpdateRole = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, role }) => userService.updateRole(userId, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useUpdateStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, enabled }) => userService.updateStatus(userId, enabled),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: userService.deleteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};
