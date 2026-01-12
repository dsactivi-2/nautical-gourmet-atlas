import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Image,
  TextInput,
  Modal,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { partnersApi, favoritesApi } from '../../src/api';
import { Card, Badge, LoadingState, ErrorState, Button } from '../../src/components/ui';
import type { PartnerListItem, Category, Filter } from '../../src/types';
import { useAuthStore } from '../../src/hooks/useAuthStore';

// Default BBOX for Croatia (Dalmatian coast)
const DEFAULT_BBOX = '13.5,42.5,17.5,45.5';

export default function MapScreen() {
  const router = useRouter();
  const { t } = useTranslation();
  const { isAuthenticated } = useAuthStore();

  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);
  const [selectedFilterIds, setSelectedFilterIds] = useState<number[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [showList, setShowList] = useState(false);

  // Fetch categories
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: partnersApi.getCategories,
  });

  // Fetch filters for selected category
  const { data: filters = [] } = useQuery({
    queryKey: ['filters', selectedCategoryId],
    queryFn: () => partnersApi.getFilters(selectedCategoryId ?? undefined),
    enabled: showFilters,
  });

  // Fetch partners
  const {
    data: partners = [],
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['partners', DEFAULT_BBOX, selectedCategoryId, selectedFilterIds, searchQuery],
    queryFn: () =>
      partnersApi.getPartners({
        bbox: DEFAULT_BBOX,
        category_id: selectedCategoryId ?? undefined,
        filter_ids: selectedFilterIds.length > 0 ? selectedFilterIds.join(',') : undefined,
        q: searchQuery || undefined,
      }),
  });

  const toggleFilter = (filterId: number) => {
    setSelectedFilterIds((prev) =>
      prev.includes(filterId) ? prev.filter((id) => id !== filterId) : [...prev, filterId]
    );
  };

  const clearFilters = () => {
    setSelectedFilterIds([]);
    setShowFilters(false);
  };

  const renderPartnerCard = ({ item }: { item: PartnerListItem }) => (
    <Card
      testID={`map_partner_card_${item.id}`}
      style={styles.partnerCard}
      onPress={() => router.push(`/partner/${item.id}`)}
    >
      {item.primary_image && (
        <Image source={{ uri: item.primary_image }} style={styles.partnerImage} />
      )}
      <View style={styles.partnerInfo}>
        <View style={styles.partnerHeader}>
          <Text style={styles.partnerName} numberOfLines={1}>
            {item.name}
          </Text>
          {item.is_premium && <Badge label="Premium" variant="premium" size="small" />}
        </View>
        {item.city && <Text style={styles.partnerCity}>{item.city}</Text>}
        {item.discount_percent > 0 && (
          <Text style={styles.discount}>
            {t('partner.discount', { percent: item.discount_percent })}
          </Text>
        )}
      </View>
    </Card>
  );

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState onRetry={refetch} />;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <TextInput
          testID="map_input_search"
          style={styles.searchInput}
          placeholder={t('map.searchPartners')}
          placeholderTextColor="#94a3b8"
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        <TouchableOpacity
          testID="map_button_filters"
          style={styles.filterButton}
          onPress={() => setShowFilters(true)}
        >
          <Text style={styles.filterIcon}>⚙️</Text>
        </TouchableOpacity>
      </View>

      {/* Category Chips */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.categoriesContainer}
        contentContainerStyle={styles.categoriesContent}
      >
        <TouchableOpacity
          testID="map_category_all"
          style={[styles.categoryChip, !selectedCategoryId && styles.categoryChipActive]}
          onPress={() => setSelectedCategoryId(null)}
        >
          <Text style={[styles.categoryText, !selectedCategoryId && styles.categoryTextActive]}>
            {t('map.premiumPartners')}
          </Text>
        </TouchableOpacity>
        {categories.map((cat) => (
          <TouchableOpacity
            key={cat.id}
            testID={`map_category_${cat.slug}`}
            style={[styles.categoryChip, selectedCategoryId === cat.id && styles.categoryChipActive]}
            onPress={() => setSelectedCategoryId(cat.id)}
          >
            <Text
              style={[
                styles.categoryText,
                selectedCategoryId === cat.id && styles.categoryTextActive,
              ]}
            >
              {cat.name}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Map Placeholder */}
      <View style={styles.mapPlaceholder}>
        <Text style={styles.mapText}>🗺 Map View</Text>
        <Text style={styles.mapSubtext}>
          {t('map.results', { count: partners.length })}
        </Text>
        {partners.slice(0, 5).map((p) => (
          <TouchableOpacity
            key={p.id}
            style={styles.mapPin}
            onPress={() => router.push(`/partner/${p.id}`)}
          >
            <Text style={styles.pinText}>📍 {p.name}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Bottom Sheet */}
      <View style={styles.bottomSheet}>
        <TouchableOpacity
          testID="map_button_showList"
          style={styles.showListButton}
          onPress={() => setShowList(!showList)}
        >
          <Text style={styles.showListText}>
            {t('map.results', { count: partners.length })} - {t('map.showList')}
          </Text>
        </TouchableOpacity>

        {showList && (
          <FlatList
            data={partners}
            keyExtractor={(item) => item.id.toString()}
            renderItem={renderPartnerCard}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
          />
        )}
      </View>

      {/* Filter Modal */}
      <Modal visible={showFilters} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{t('map.filters')}</Text>
              <TouchableOpacity onPress={() => setShowFilters(false)}>
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.filtersList}>
              {filters.map((filter) => (
                <TouchableOpacity
                  key={filter.id}
                  testID={`map_filter_${filter.slug}`}
                  style={[
                    styles.filterItem,
                    selectedFilterIds.includes(filter.id) && styles.filterItemActive,
                  ]}
                  onPress={() => toggleFilter(filter.id)}
                >
                  <Text
                    style={[
                      styles.filterText,
                      selectedFilterIds.includes(filter.id) && styles.filterTextActive,
                    ]}
                  >
                    {filter.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <View style={styles.modalActions}>
              <Button
                title={t('map.clearFilters')}
                onPress={clearFilters}
                variant="outline"
                style={styles.modalButton}
              />
              <Button
                title={t('map.applyFilters')}
                onPress={() => setShowFilters(false)}
                variant="primary"
                style={styles.modalButton}
              />
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 12,
  },
  searchInput: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  filterButton: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  filterIcon: {
    fontSize: 20,
  },
  categoriesContainer: {
    maxHeight: 50,
  },
  categoriesContent: {
    paddingHorizontal: 16,
    gap: 8,
  },
  categoryChip: {
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    marginRight: 8,
  },
  categoryChipActive: {
    backgroundColor: '#1a365d',
    borderColor: '#1a365d',
  },
  categoryText: {
    fontSize: 14,
    color: '#64748b',
    fontWeight: '500',
  },
  categoryTextActive: {
    color: '#fff',
  },
  mapPlaceholder: {
    flex: 1,
    backgroundColor: '#e0f2fe',
    margin: 16,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  mapText: {
    fontSize: 48,
    marginBottom: 8,
  },
  mapSubtext: {
    fontSize: 16,
    color: '#0369a1',
    marginBottom: 16,
  },
  mapPin: {
    backgroundColor: '#fff',
    padding: 8,
    borderRadius: 8,
    marginVertical: 4,
  },
  pinText: {
    fontSize: 14,
    color: '#1e293b',
  },
  bottomSheet: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 16,
    maxHeight: '50%',
  },
  showListButton: {
    alignItems: 'center',
    paddingVertical: 8,
  },
  showListText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1a365d',
  },
  listContent: {
    paddingTop: 8,
  },
  partnerCard: {
    flexDirection: 'row',
    padding: 12,
    marginBottom: 12,
  },
  partnerImage: {
    width: 80,
    height: 80,
    borderRadius: 12,
    backgroundColor: '#e2e8f0',
  },
  partnerInfo: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'center',
  },
  partnerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  partnerName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    flex: 1,
  },
  partnerCity: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
  discount: {
    fontSize: 14,
    fontWeight: '600',
    color: '#16a34a',
    marginTop: 4,
  },
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    maxHeight: '70%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1e293b',
  },
  closeButton: {
    fontSize: 24,
    color: '#64748b',
  },
  filtersList: {
    maxHeight: 300,
  },
  filterItem: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    marginBottom: 8,
    backgroundColor: '#f8fafc',
  },
  filterItemActive: {
    backgroundColor: '#e0f2fe',
  },
  filterText: {
    fontSize: 16,
    color: '#64748b',
  },
  filterTextActive: {
    color: '#0369a1',
    fontWeight: '600',
  },
  modalActions: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
  },
  modalButton: {
    flex: 1,
  },
});
