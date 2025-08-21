import { computed, readonly } from 'vue';
import Member, { type UserRole } from '@/features/member/entity/Member';

export const useAuth = () => {
  const getCurrentUser = (): Member | null => {
    try {
      const userStr = localStorage.getItem('user');
      if (!userStr) return null;
      
      const userData = JSON.parse(userStr);
      return Member.fromResponse(userData);
    } catch {
      return null;
    }
  };

  const user = computed(() => getCurrentUser());
  
  const isLoggedIn = computed(() => user.value !== null);
  
  const isAdmin = computed(() => user.value?.isAdmin() ?? false);
  
  const isUser = computed(() => user.value?.isUser() ?? false);
  
  const hasRole = (role: UserRole) => {
    return user.value?.role === role;
  };

  const canCreateNotice = computed(() => isAdmin.value);
  
  const canEditNotice = computed(() => isAdmin.value);
  
  const canDeleteNotice = computed(() => isAdmin.value);

  return {
    user: readonly(user),
    isLoggedIn: readonly(isLoggedIn),
    isAdmin: readonly(isAdmin),
    isUser: readonly(isUser),
    hasRole,
    canCreateNotice: readonly(canCreateNotice),
    canEditNotice: readonly(canEditNotice),
    canDeleteNotice: readonly(canDeleteNotice),
  };
};