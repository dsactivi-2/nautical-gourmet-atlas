import {
  getStoredLanguage,
  setStoredLanguage,
  getAccessToken,
  storeTokens,
  clearTokens,
  STORAGE_KEYS,
} from '../../src/api/client';
import * as SecureStore from 'expo-secure-store';

jest.mock('expo-secure-store');

describe('API Client Storage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getStoredLanguage', () => {
    it('returns stored language', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('hr');

      const lang = await getStoredLanguage();

      expect(lang).toBe('hr');
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith(STORAGE_KEYS.LANGUAGE);
    });

    it('returns default "en" when no language stored', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);

      const lang = await getStoredLanguage();

      expect(lang).toBe('en');
    });

    it('returns "en" on error', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const lang = await getStoredLanguage();

      expect(lang).toBe('en');
    });
  });

  describe('setStoredLanguage', () => {
    it('stores language correctly', async () => {
      await setStoredLanguage('de');

      expect(SecureStore.setItemAsync).toHaveBeenCalledWith(STORAGE_KEYS.LANGUAGE, 'de');
    });
  });

  describe('getAccessToken', () => {
    it('returns stored token', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue('test-token');

      const token = await getAccessToken();

      expect(token).toBe('test-token');
      expect(SecureStore.getItemAsync).toHaveBeenCalledWith(STORAGE_KEYS.ACCESS_TOKEN);
    });

    it('returns null when no token stored', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockResolvedValue(null);

      const token = await getAccessToken();

      expect(token).toBeNull();
    });

    it('returns null on error', async () => {
      (SecureStore.getItemAsync as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const token = await getAccessToken();

      expect(token).toBeNull();
    });
  });

  describe('storeTokens', () => {
    it('stores both tokens correctly', async () => {
      await storeTokens('access-token', 'refresh-token');

      expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
        STORAGE_KEYS.ACCESS_TOKEN,
        'access-token'
      );
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith(
        STORAGE_KEYS.REFRESH_TOKEN,
        'refresh-token'
      );
    });
  });

  describe('clearTokens', () => {
    it('deletes both tokens', async () => {
      await clearTokens();

      expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith(STORAGE_KEYS.ACCESS_TOKEN);
      expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith(STORAGE_KEYS.REFRESH_TOKEN);
    });
  });
});
