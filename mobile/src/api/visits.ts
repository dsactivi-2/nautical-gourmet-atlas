import { apiClient } from './client';
import type { Visit, VisitCreate, VisitUpdate } from '../types';

export const visitsApi = {
  // List visits
  getVisits: async (discountUsedOnly: boolean = false): Promise<Visit[]> => {
    const response = await apiClient.get<Visit[]>('/visits', {
      params: discountUsedOnly ? { discount_used_only: true } : undefined,
    });
    return response.data;
  },

  // Create visit
  createVisit: async (data: VisitCreate): Promise<Visit> => {
    const response = await apiClient.post<Visit>('/visits', data);
    return response.data;
  },

  // Update visit (mark discount used)
  updateVisit: async (visitId: number, data: VisitUpdate): Promise<Visit> => {
    const response = await apiClient.patch<Visit>(`/visits/${visitId}`, data);
    return response.data;
  },
};
