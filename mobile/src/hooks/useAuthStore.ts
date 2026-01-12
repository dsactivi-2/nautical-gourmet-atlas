import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import { STORAGE_KEYS, clearTokens, getAccessToken } from '../api/client';
import { authApi } from '../api/auth';
import type { User, UserCreate, UserLogin, UserUpdate } from '../types';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  initialize: () => Promise<void>;
  login: (data: UserLogin) => Promise<void>;
  register: (data: UserCreate) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: UserUpdate) => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  initialize: async () => {
    try {
      const token = await getAccessToken();
      if (token) {
        const user = await authApi.getMe();
        set({ user, isAuthenticated: true, isLoading: false });
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } catch {
      // Token invalid or expired
      await clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  login: async (data: UserLogin) => {
    const response = await authApi.login(data);
    set({ user: response.user, isAuthenticated: true });
  },

  register: async (data: UserCreate) => {
    const response = await authApi.register(data);
    set({ user: response.user, isAuthenticated: true });
  },

  logout: async () => {
    await authApi.logout();
    set({ user: null, isAuthenticated: false });
  },

  updateProfile: async (data: UserUpdate) => {
    const user = await authApi.updateMe(data);
    set({ user });
  },

  setUser: (user: User | null) => {
    set({ user, isAuthenticated: !!user });
  },
}));
