import { defineStore } from 'pinia';

interface User {
  name: string;
  username: string;
}

interface AuthState {
  user: User | null;
}

function getStoredUser(): User | null {
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    try {
      return JSON.parse(storedUser);
    } catch (e) {
      console.error('Failed to parse user from localStorage', e);
      localStorage.removeItem('user');
      return null;
    }
  }
  return null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: getStoredUser(),
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    currentUser: (state) => state.user,
  },

  actions: {
    setUser(user: User) {
      this.user = user;
      localStorage.setItem('user', JSON.stringify(user));
    },

    logout() {
      this.user = null;
      localStorage.removeItem('user');
    },
  },
});
