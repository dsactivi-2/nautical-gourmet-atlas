// User types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  country?: string;
  dob?: string;
  gender?: 'male' | 'female' | 'other';
  is_nautical: boolean;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  country?: string;
  dob?: string;
  gender?: 'male' | 'female' | 'other';
  is_nautical?: boolean;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserUpdate {
  first_name?: string;
  last_name?: string;
  country?: string;
  dob?: string;
  gender?: 'male' | 'female' | 'other';
  is_nautical?: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// Category types
export interface Category {
  id: number;
  slug: string;
  name: string;
  description?: string;
  icon?: string;
  sort_order: number;
}

// Filter types
export interface Filter {
  id: number;
  category_id: number;
  slug: string;
  name: string;
  icon?: string;
  sort_order: number;
}

// Partner types
export interface PartnerImage {
  id: number;
  url: string;
  alt_text?: string;
  is_primary: boolean;
  sort_order: number;
}

export interface PartnerFilter {
  id: number;
  slug: string;
  name: string;
}

export interface PartnerListItem {
  id: number;
  slug: string;
  name: string;
  category_id: number;
  category_slug?: string;
  latitude?: number;
  longitude?: number;
  city?: string;
  is_premium: boolean;
  discount_percent: number;
  primary_image?: string;
  is_favorite: boolean;
}

export interface PartnerDetail {
  id: number;
  slug: string;
  name: string;
  description?: string;
  category_id: number;
  category_slug?: string;
  category_name?: string;
  latitude?: number;
  longitude?: number;
  address?: string;
  city?: string;
  country?: string;
  phone?: string;
  email?: string;
  website?: string;
  is_premium: boolean;
  discount_percent: number;
  pin_code?: string;
  opening_hours?: Record<string, string>;
  images: PartnerImage[];
  filters: PartnerFilter[];
  is_favorite: boolean;
  created_at: string;
}

// Favorite types
export interface Favorite {
  id: number;
  partner_id: number;
  partner_name?: string;
  partner_slug?: string;
  partner_image?: string;
  partner_is_premium: boolean;
  partner_category_slug?: string;
  created_at: string;
}

export interface FavoriteCreate {
  partner_id: number;
}

// Visit types
export interface Visit {
  id: number;
  partner_id: number;
  partner_name?: string;
  partner_slug?: string;
  discount_used: boolean;
  visited_at: string;
}

export interface VisitCreate {
  partner_id: number;
  discount_used?: boolean;
}

export interface VisitUpdate {
  discount_used: boolean;
}

// Treasure types
export type TreasureCategory = 'wines' | 'traditional_dishes' | 'products' | 'crafts_souvenirs';

export interface TreasureListItem {
  id: number;
  slug: string;
  title: string;
  category: TreasureCategory;
  image_url?: string;
}

export interface RelatedPartner {
  id: number;
  slug: string;
  name: string;
  is_premium: boolean;
  primary_image?: string;
}

export interface TreasureDetail {
  id: number;
  slug: string;
  title: string;
  content?: string;
  category: TreasureCategory;
  image_url?: string;
  video_url?: string;
  related_partners: RelatedPartner[];
  created_at: string;
}

// API params
export interface PartnerSearchParams {
  bbox?: string;
  category_id?: number;
  filter_ids?: string;
  q?: string;
  premium_only?: boolean;
  limit?: number;
  offset?: number;
}
