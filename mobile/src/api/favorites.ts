import { apiClient } from './client';
import type { Favorite, FavoriteCreate } from '../types';

export const favoritesApi = {
  // List favorites
  getFavorites: async (): Promise<Favorite[]> => {
    const response = await apiClient.get<Favorite[]>('/favorites');
    return response.data;
  },

  // Add favorite
  addFavorite: async (data: FavoriteCreate): Promise<Favorite> => {
    const response = await apiClient.post<Favorite>('/favorites', data);
    return response.data;
  },

  // Remove favorite
  removeFavorite: async (favoriteId: number): Promise<void> => {
    await apiClient.delete(`/favorites/${favoriteId}`);
  },
};
