import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, Image, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { treasuresApi } from '../../src/api';
import { Card, LoadingState, ErrorState } from '../../src/components/ui';
import type { TreasureListItem, TreasureCategory } from '../../src/types';

const TREASURE_CATEGORIES: { key: TreasureCategory; emoji: string }[] = [
  { key: 'wines', emoji: '🍷' },
  { key: 'traditional_dishes', emoji: '🍽' },
  { key: 'products', emoji: '🧀' },
  { key: 'crafts_souvenirs', emoji: '🎨' },
];

export default function TreasuresScreen() {
  const router = useRouter();
  const { t } = useTranslation();
  const [selectedCategory, setSelectedCategory] = useState<TreasureCategory | null>(null);

  const {
    data: treasures = [],
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['treasures', selectedCategory],
    queryFn: () => treasuresApi.getTreasures(selectedCategory ?? undefined),
  });

  const renderCategoryCard = ({ item }: { item: { key: TreasureCategory; emoji: string } }) => (
    <TouchableOpacity
      testID={`treasures_category_${item.key}`}
      style={[styles.categoryCard, selectedCategory === item.key && styles.categoryCardActive]}
      onPress={() => setSelectedCategory(selectedCategory === item.key ? null : item.key)}
    >
      <Text style={styles.categoryEmoji}>{item.emoji}</Text>
      <Text style={[styles.categoryName, selectedCategory === item.key && styles.categoryNameActive]}>
        {t(`treasures.${item.key}`)}
      </Text>
    </TouchableOpacity>
  );

  const renderTreasureCard = ({ item }: { item: TreasureListItem }) => (
    <Card
      testID={`treasures_card_${item.id}`}
      style={styles.treasureCard}
      onPress={() => router.push(`/treasure/${item.id}`)}
    >
      {item.image_url && (
        <Image source={{ uri: item.image_url }} style={styles.treasureImage} />
      )}
      <View style={styles.treasureInfo}>
        <Text style={styles.treasureTitle} numberOfLines={2}>
          {item.title}
        </Text>
        <Text style={styles.treasureCategory}>
          {t(`treasures.${item.category}`)}
        </Text>
      </View>
    </Card>
  );

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState onRetry={refetch} />;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.headerContainer}>
        <Text style={styles.title}>{t('treasures.title')}</Text>
      </View>

      {/* Category Grid */}
      <FlatList
        data={TREASURE_CATEGORIES}
        keyExtractor={(item) => item.key}
        renderItem={renderCategoryCard}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.categoriesContainer}
      />

      {/* Treasures List */}
      <FlatList
        data={treasures}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderTreasureCard}
        numColumns={2}
        contentContainerStyle={styles.listContent}
        columnWrapperStyle={styles.row}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  headerContainer: {
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1a365d',
  },
  categoriesContainer: {
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  categoryCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginRight: 12,
    alignItems: 'center',
    width: 100,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  categoryCardActive: {
    borderColor: '#1a365d',
    backgroundColor: '#e0f2fe',
  },
  categoryEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  categoryName: {
    fontSize: 12,
    fontWeight: '500',
    color: '#64748b',
    textAlign: 'center',
  },
  categoryNameActive: {
    color: '#1a365d',
    fontWeight: '600',
  },
  listContent: {
    padding: 16,
  },
  row: {
    justifyContent: 'space-between',
  },
  treasureCard: {
    width: '48%',
    marginBottom: 16,
    padding: 0,
    overflow: 'hidden',
  },
  treasureImage: {
    width: '100%',
    height: 120,
    backgroundColor: '#e2e8f0',
  },
  treasureInfo: {
    padding: 12,
  },
  treasureTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 4,
  },
  treasureCategory: {
    fontSize: 12,
    color: '#64748b',
  },
});
