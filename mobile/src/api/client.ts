import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

const API_BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl || 'http://localhost:8000/v1';

// Storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  LANGUAGE: 'language',
};

// Get stored language
export const getStoredLanguage = async (): Promise<string> => {
  try {
    const lang = await SecureStore.getItemAsync(STORAGE_KEYS.LANGUAGE);
    return lang || 'en';
  } catch {
    return 'en';
  }
};

// Set language
export const setStoredLanguage = async (lang: string): Promise<void> => {
  await SecureStore.setItemAsync(STORAGE_KEYS.LANGUAGE, lang);
};

// Get stored token
export const getAccessToken = async (): Promise<string | null> => {
  try {
    return await SecureStore.getItemAsync(STORAGE_KEYS.ACCESS_TOKEN);
  } catch {
    return null;
  }
};

// Store tokens
export const storeTokens = async (accessToken: string, refreshToken: string): Promise<void> => {
  await SecureStore.setItemAsync(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
  await SecureStore.setItemAsync(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
};

// Clear tokens
export const clearTokens = async (): Promise<void> => {
  await SecureStore.deleteItemAsync(STORAGE_KEYS.ACCESS_TOKEN);
  await SecureStore.deleteItemAsync(STORAGE_KEYS.REFRESH_TOKEN);
};

// Create axios instance
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 15000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor
  client.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      // Add language header
      const lang = await getStoredLanguage();
      config.headers['Accept-Language'] = lang;

      // Add auth header if token exists
      const token = await getAccessToken();
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }

      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (error.response?.status === 401) {
        // Token expired or invalid - clear and redirect to login
        await clearTokens();
        // Note: Navigation to login should be handled by auth state listener
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const apiClient = createApiClient();

// Type-safe API error handling
export interface ApiError {
  detail: string;
  status: number;
}

export const getApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    return {
      detail: error.response?.data?.detail || error.message || 'An error occurred',
      status: error.response?.status || 500,
    };
  }
  return {
    detail: 'An unexpected error occurred',
    status: 500,
  };
};
