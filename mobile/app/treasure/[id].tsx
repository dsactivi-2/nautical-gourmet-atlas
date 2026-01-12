import React from 'react';
import { View, Text, StyleSheet, ScrollView, Image, FlatList } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { treasuresApi } from '../../src/api';
import { Card, Badge, LoadingState, ErrorState } from '../../src/components/ui';
import type { RelatedPartner } from '../../src/types';

export default function TreasureDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const { t } = useTranslation();

  const treasureId = parseInt(id, 10);

  const {
    data: treasure,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['treasure', treasureId],
    queryFn: () => treasuresApi.getTreasure(treasureId),
    enabled: !!treasureId,
  });

  const renderRelatedPartner = ({ item }: { item: RelatedPartner }) => (
    <Card
      testID={`treasure_related_partner_${item.id}`}
      style={styles.partnerCard}
      onPress={() => router.push(`/partner/${item.id}`)}
    >
      {item.primary_image && (
        <Image source={{ uri: item.primary_image }} style={styles.partnerImage} />
      )}
      <View style={styles.partnerInfo}>
        <Text style={styles.partnerName} numberOfLines={1}>
          {item.name}
        </Text>
        {item.is_premium && <Badge label="Premium" variant="premium" size="small" />}
      </View>
    </Card>
  );

  if (isLoading) return <LoadingState />;
  if (isError || !treasure) return <ErrorState onRetry={refetch} />;

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Hero Image */}
      {treasure.image_url && (
        <Image source={{ uri: treasure.image_url }} style={styles.heroImage} />
      )}

      {/* Content */}
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Badge label={t(`treasures.${treasure.category}`)} variant="primary" />
          <Text style={styles.title}>{treasure.title}</Text>
        </View>

        {/* Description */}
        {treasure.content && (
          <View style={styles.section}>
            <Text style={styles.description}>{treasure.content}</Text>
          </View>
        )}

        {/* Related Partners */}
        {treasure.related_partners.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>{t('treasures.relatedPartners')}</Text>
            <FlatList
              data={treasure.related_partners}
              keyExtractor={(item) => item.id.toString()}
              renderItem={renderRelatedPartner}
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.partnersContainer}
            />
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  heroImage: {
    width: '100%',
    height: 250,
    backgroundColor: '#e2e8f0',
  },
  content: {
    padding: 16,
  },
  header: {
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1e293b',
    marginTop: 12,
    lineHeight: 36,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 12,
  },
  description: {
    fontSize: 16,
    color: '#475569',
    lineHeight: 26,
  },
  partnersContainer: {
    paddingVertical: 8,
  },
  partnerCard: {
    width: 160,
    marginRight: 12,
    padding: 0,
    overflow: 'hidden',
  },
  partnerImage: {
    width: '100%',
    height: 100,
    backgroundColor: '#e2e8f0',
  },
  partnerInfo: {
    padding: 12,
  },
  partnerName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 4,
  },
});
