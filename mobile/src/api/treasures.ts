import { apiClient } from './client';
import type { TreasureListItem, TreasureDetail, TreasureCategory } from '../types';

export const treasuresApi = {
  // List treasures
  getTreasures: async (category?: TreasureCategory): Promise<TreasureListItem[]> => {
    const response = await apiClient.get<TreasureListItem[]>('/treasures', {
      params: category ? { category } : undefined,
    });
    return response.data;
  },

  // Get treasure categories
  getTreasureCategories: async (): Promise<{ slug: string; name: string }[]> => {
    const response = await apiClient.get<{ slug: string; name: string }[]>('/treasures/categories');
    return response.data;
  },

  // Get treasure details
  getTreasure: async (treasureId: number): Promise<TreasureDetail> => {
    const response = await apiClient.get<TreasureDetail>(`/treasures/${treasureId}`);
    return response.data;
  },
};
