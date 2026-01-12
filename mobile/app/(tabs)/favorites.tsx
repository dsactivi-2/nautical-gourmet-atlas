import React from 'react';
import { View, Text, StyleSheet, FlatList, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { favoritesApi } from '../../src/api';
import { Card, Badge, LoadingState, ErrorState, EmptyState } from '../../src/components/ui';
import type { Favorite } from '../../src/types';
import { useAuthStore } from '../../src/hooks/useAuthStore';

export default function FavoritesScreen() {
  const router = useRouter();
  const { t } = useTranslation();
  const { isAuthenticated } = useAuthStore();

  const {
    data: favorites = [],
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['favorites'],
    queryFn: favoritesApi.getFavorites,
    enabled: isAuthenticated,
  });

  const renderFavoriteCard = ({ item }: { item: Favorite }) => (
    <Card
      testID={`favorites_card_${item.id}`}
      style={styles.card}
      onPress={() => router.push(`/partner/${item.partner_id}`)}
    >
      {item.partner_image && (
        <Image source={{ uri: item.partner_image }} style={styles.image} />
      )}
      <View style={styles.info}>
        <View style={styles.header}>
          <Text style={styles.name} numberOfLines={1}>
            {item.partner_name}
          </Text>
          {item.partner_is_premium && <Badge label="Premium" variant="premium" size="small" />}
        </View>
        <Text style={styles.date}>
          {new Date(item.created_at).toLocaleDateString()}
        </Text>
      </View>
    </Card>
  );

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container}>
        <EmptyState
          title={t('auth.login')}
          description="Login to see your favorites"
          actionLabel={t('auth.login')}
          onAction={() => router.push('/(auth)/login')}
        />
      </SafeAreaView>
    );
  }

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState onRetry={refetch} />;

  if (favorites.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.headerContainer}>
          <Text style={styles.title}>{t('favorites.title')}</Text>
        </View>
        <EmptyState
          title={t('favorites.empty')}
          description={t('favorites.emptyDescription')}
          actionLabel={t('favorites.explore')}
          onAction={() => router.push('/(tabs)/map')}
        />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.headerContainer}>
        <Text style={styles.title}>{t('favorites.title')}</Text>
      </View>
      <FlatList
        data={favorites}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderFavoriteCard}
        contentContainerStyle={styles.listContent}
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
  listContent: {
    padding: 16,
  },
  card: {
    flexDirection: 'row',
    padding: 12,
    marginBottom: 12,
  },
  image: {
    width: 80,
    height: 80,
    borderRadius: 12,
    backgroundColor: '#e2e8f0',
  },
  info: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    flex: 1,
  },
  date: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
});
