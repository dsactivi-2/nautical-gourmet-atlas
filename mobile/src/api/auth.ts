import { apiClient, storeTokens, clearTokens } from './client';
import type { UserCreate, UserLogin, TokenResponse, User, UserUpdate } from '../types';

export const authApi = {
  // Register new user
  register: async (data: UserCreate): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/register', data);
    await storeTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  },

  // Login
  login: async (data: UserLogin): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', data);
    await storeTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  },

  // Refresh token
  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/refresh', null, {
      params: { refresh_token: refreshToken },
    });
    await storeTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  },

  // Logout
  logout: async (): Promise<void> => {
    await clearTokens();
  },

  // Get current user
  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/me');
    return response.data;
  },

  // Update current user
  updateMe: async (data: UserUpdate): Promise<User> => {
    const response = await apiClient.patch<User>('/me', data);
    return response.data;
  },
};
