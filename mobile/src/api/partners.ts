import { apiClient } from './client';
import type { PartnerListItem, PartnerDetail, PartnerSearchParams, Category, Filter } from '../types';

export const partnersApi = {
  // List categories
  getCategories: async (): Promise<Category[]> => {
    const response = await apiClient.get<Category[]>('/categories');
    return response.data;
  },

  // Get filters by category
  getFilters: async (categoryId?: number): Promise<Filter[]> => {
    const response = await apiClient.get<Filter[]>('/filters', {
      params: categoryId ? { category_id: categoryId } : undefined,
    });
    return response.data;
  },

  // List partners with search/filter
  getPartners: async (params: PartnerSearchParams = {}): Promise<PartnerListItem[]> => {
    const response = await apiClient.get<PartnerListItem[]>('/partners', { params });
    return response.data;
  },

  // Get partner details
  getPartner: async (partnerId: number): Promise<PartnerDetail> => {
    const response = await apiClient.get<PartnerDetail>(`/partners/${partnerId}`);
    return response.data;
  },
};
