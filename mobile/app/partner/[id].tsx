import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  Modal,
  Linking,
  Alert,
} from 'react-native';
import { useLocalSearchParams, Stack } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { partnersApi, favoritesApi, visitsApi } from '../../src/api';
import { Badge, Button, LoadingState, ErrorState, Card } from '../../src/components/ui';
import { useAuthStore } from '../../src/hooks/useAuthStore';

export default function PartnerDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuthStore();

  const [showPin, setShowPin] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const partnerId = parseInt(id, 10);

  const {
    data: partner,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['partner', partnerId],
    queryFn: () => partnersApi.getPartner(partnerId),
    enabled: !!partnerId,
  });

  // Add favorite mutation
  const addFavoriteMutation = useMutation({
    mutationFn: () => favoritesApi.addFavorite({ partner_id: partnerId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['partner', partnerId] });
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    },
  });

  // Create visit mutation
  const createVisitMutation = useMutation({
    mutationFn: (discountUsed: boolean) =>
      visitsApi.createVisit({ partner_id: partnerId, discount_used: discountUsed }),
    onSuccess: () => {
      Alert.alert('Success', 'Visit recorded!');
      setShowPin(false);
    },
  });

  const handleCall = () => {
    if (partner?.phone) {
      Linking.openURL(`tel:${partner.phone}`);
    }
  };

  const handleWebsite = () => {
    if (partner?.website) {
      Linking.openURL(partner.website);
    }
  };

  const handleFavorite = () => {
    if (!isAuthenticated) {
      Alert.alert('Login Required', 'Please login to save favorites');
      return;
    }
    addFavoriteMutation.mutate();
  };

  const handleMarkUsed = () => {
    if (!isAuthenticated) {
      Alert.alert('Login Required', 'Please login to use discounts');
      return;
    }
    createVisitMutation.mutate(true);
  };

  if (isLoading) return <LoadingState />;
  if (isError || !partner) return <ErrorState onRetry={refetch} />;

  return (
    <>
      <Stack.Screen
        options={{
          headerRight: () => (
            <TouchableOpacity
              testID="partner_button_favorite"
              onPress={handleFavorite}
              style={styles.headerButton}
            >
              <Text style={styles.headerIcon}>{partner.is_favorite ? '❤️' : '🤍'}</Text>
            </TouchableOpacity>
          ),
        }}
      />

      <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
        {/* Image Gallery */}
        {partner.images.length > 0 && (
          <View style={styles.gallery}>
            <Image
              source={{ uri: partner.images[currentImageIndex]?.url }}
              style={styles.mainImage}
            />
            {partner.images.length > 1 && (
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                style={styles.thumbnails}
              >
                {partner.images.map((img, idx) => (
                  <TouchableOpacity
                    key={img.id}
                    onPress={() => setCurrentImageIndex(idx)}
                    style={[
                      styles.thumbnail,
                      idx === currentImageIndex && styles.thumbnailActive,
                    ]}
                  >
                    <Image source={{ uri: img.url }} style={styles.thumbnailImage} />
                  </TouchableOpacity>
                ))}
              </ScrollView>
            )}
          </View>
        )}

        {/* Content */}
        <View style={styles.content}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.name}>{partner.name}</Text>
            <View style={styles.badges}>
              {partner.is_premium && <Badge label="Premium" variant="premium" />}
              {partner.category_name && (
                <Badge label={partner.category_name} variant="secondary" />
              )}
            </View>
          </View>

          {/* Filters */}
          {partner.filters.length > 0 && (
            <View style={styles.filters}>
              {partner.filters.map((f) => (
                <Badge key={f.id} label={f.name} variant="primary" size="small" />
              ))}
            </View>
          )}

          {/* Discount Block */}
          {partner.is_premium && partner.discount_percent > 0 && (
            <Card style={styles.discountCard}>
              <Text style={styles.discountTitle}>
                {t('partner.premiumDiscount', { percent: partner.discount_percent })}
              </Text>
              <Button
                testID="partner_button_showPin"
                title={t('partner.showPin')}
                onPress={() => setShowPin(true)}
                variant="primary"
                disabled={!isAuthenticated}
              />
              {!isAuthenticated && (
                <Text style={styles.loginHint}>Login to see PIN</Text>
              )}
            </Card>
          )}

          {/* Description */}
          {partner.description && (
            <View style={styles.section}>
              <Text style={styles.description}>{partner.description}</Text>
            </View>
          )}

          {/* Opening Hours */}
          {partner.opening_hours && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>{t('partner.openingHours')}</Text>
              {Object.entries(partner.opening_hours).map(([day, hours]) => (
                <View key={day} style={styles.hoursRow}>
                  <Text style={styles.hoursDay}>{day}</Text>
                  <Text style={styles.hoursTime}>{hours as string}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Location */}
          {(partner.address || partner.city) && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Location</Text>
              <Text style={styles.address}>
                {partner.address}
                {partner.city && `, ${partner.city}`}
                {partner.country && `, ${partner.country}`}
              </Text>
            </View>
          )}

          {/* Actions */}
          <View style={styles.actions}>
            {partner.phone && (
              <Button
                testID="partner_button_call"
                title={t('partner.call')}
                onPress={handleCall}
                variant="outline"
                style={styles.actionButton}
              />
            )}
            {partner.website && (
              <Button
                testID="partner_button_website"
                title={t('partner.website')}
                onPress={handleWebsite}
                variant="outline"
                style={styles.actionButton}
              />
            )}
          </View>
        </View>
      </ScrollView>

      {/* PIN Modal */}
      <Modal visible={showPin} animationType="fade" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>{t('partner.showPin')}</Text>
            <View style={styles.pinBox}>
              <Text style={styles.pinCode}>{partner.pin_code || '----'}</Text>
            </View>
            <Text style={styles.pinWarning}>{t('partner.pinWarning')}</Text>

            <TouchableOpacity
              testID="partner_button_markUsed"
              style={styles.markUsedButton}
              onPress={handleMarkUsed}
            >
              <Text style={styles.markUsedText}>☑ {t('partner.markUsed')}</Text>
            </TouchableOpacity>

            <Button
              title={t('common.cancel')}
              onPress={() => setShowPin(false)}
              variant="ghost"
            />
          </View>
        </View>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  headerButton: {
    padding: 8,
  },
  headerIcon: {
    fontSize: 24,
  },
  gallery: {
    backgroundColor: '#fff',
  },
  mainImage: {
    width: '100%',
    height: 250,
    backgroundColor: '#e2e8f0',
  },
  thumbnails: {
    padding: 12,
  },
  thumbnail: {
    marginRight: 8,
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  thumbnailActive: {
    borderColor: '#1a365d',
  },
  thumbnailImage: {
    width: 60,
    height: 60,
    backgroundColor: '#e2e8f0',
  },
  content: {
    padding: 16,
  },
  header: {
    marginBottom: 12,
  },
  name: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1e293b',
    marginBottom: 8,
  },
  badges: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
  },
  filters: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
    marginBottom: 16,
  },
  discountCard: {
    backgroundColor: '#fef3c7',
    marginBottom: 16,
  },
  discountTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#b45309',
    marginBottom: 12,
  },
  loginHint: {
    fontSize: 12,
    color: '#92400e',
    marginTop: 8,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: '#475569',
    lineHeight: 24,
  },
  hoursRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  hoursDay: {
    fontSize: 14,
    color: '#64748b',
    textTransform: 'capitalize',
  },
  hoursTime: {
    fontSize: 14,
    color: '#1e293b',
  },
  address: {
    fontSize: 14,
    color: '#475569',
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
    marginBottom: 32,
  },
  actionButton: {
    flex: 1,
  },
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 24,
    padding: 24,
    width: '100%',
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 16,
  },
  pinBox: {
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    padding: 24,
    marginBottom: 16,
  },
  pinCode: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1a365d',
    letterSpacing: 4,
  },
  pinWarning: {
    fontSize: 14,
    color: '#ef4444',
    textAlign: 'center',
    marginBottom: 24,
  },
  markUsedButton: {
    paddingVertical: 12,
    marginBottom: 16,
  },
  markUsedText: {
    fontSize: 16,
    color: '#16a34a',
    fontWeight: '600',
  },
});
