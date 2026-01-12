import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuthStore } from '../../src/hooks/useAuthStore';
import { setStoredLanguage } from '../../src/api';
import { Card, Button } from '../../src/components/ui';

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'hr', name: 'Hrvatski' },
  { code: 'de', name: 'Deutsch' },
];

export default function SettingsScreen() {
  const router = useRouter();
  const { t, i18n } = useTranslation();
  const { user, isAuthenticated, logout, updateProfile } = useAuthStore();
  const [showLanguages, setShowLanguages] = useState(false);

  const handleLanguageChange = async (langCode: string) => {
    await setStoredLanguage(langCode);
    i18n.changeLanguage(langCode);
    setShowLanguages(false);
  };

  const handleLogout = () => {
    Alert.alert(
      t('auth.logout'),
      'Are you sure you want to logout?',
      [
        { text: t('common.cancel'), style: 'cancel' },
        {
          text: t('auth.logout'),
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/(auth)/welcome');
          },
        },
      ]
    );
  };

  const handleNauticalToggle = async (value: boolean) => {
    if (isAuthenticated) {
      await updateProfile({ is_nautical: value });
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>{t('settings.title')}</Text>

        {/* Profile Section */}
        {isAuthenticated && user ? (
          <Card style={styles.profileCard}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>
                {user.first_name[0]}
                {user.last_name[0]}
              </Text>
            </View>
            <View style={styles.profileInfo}>
              <Text style={styles.profileName}>
                {user.first_name} {user.last_name}
              </Text>
              <Text style={styles.profileEmail}>{user.email}</Text>
            </View>
          </Card>
        ) : (
          <Card style={styles.profileCard}>
            <Text style={styles.guestText}>Guest User</Text>
            <Button
              title={t('auth.login')}
              onPress={() => router.push('/(auth)/login')}
              variant="primary"
              size="medium"
              testID="settings_button_login"
            />
          </Card>
        )}

        {/* Language Section */}
        <Text style={styles.sectionTitle}>{t('settings.language')}</Text>
        <Card style={styles.section}>
          <TouchableOpacity
            testID="settings_button_language"
            style={styles.settingRow}
            onPress={() => setShowLanguages(!showLanguages)}
          >
            <Text style={styles.settingLabel}>{t('settings.language')}</Text>
            <Text style={styles.settingValue}>
              {LANGUAGES.find((l) => l.code === i18n.language)?.name || 'English'} ▼
            </Text>
          </TouchableOpacity>

          {showLanguages && (
            <View style={styles.languageList}>
              {LANGUAGES.map((lang) => (
                <TouchableOpacity
                  key={lang.code}
                  testID={`settings_language_${lang.code}`}
                  style={[
                    styles.languageOption,
                    i18n.language === lang.code && styles.languageOptionActive,
                  ]}
                  onPress={() => handleLanguageChange(lang.code)}
                >
                  <Text
                    style={[
                      styles.languageText,
                      i18n.language === lang.code && styles.languageTextActive,
                    ]}
                  >
                    {lang.name}
                  </Text>
                  {i18n.language === lang.code && <Text>✓</Text>}
                </TouchableOpacity>
              ))}
            </View>
          )}
        </Card>

        {/* Preferences Section */}
        {isAuthenticated && (
          <>
            <Text style={styles.sectionTitle}>{t('settings.preferences')}</Text>
            <Card style={styles.section}>
              <View style={styles.settingRow}>
                <Text style={styles.settingLabel}>{t('settings.nauticalExperiences')}</Text>
                <Switch
                  testID="settings_switch_nautical"
                  value={user?.is_nautical || false}
                  onValueChange={handleNauticalToggle}
                  trackColor={{ false: '#e2e8f0', true: '#1a365d' }}
                  thumbColor="#fff"
                />
              </View>
            </Card>
          </>
        )}

        {/* Legal Section */}
        <Text style={styles.sectionTitle}>{t('settings.legal')}</Text>
        <Card style={styles.section}>
          <TouchableOpacity style={styles.settingRow}>
            <Text style={styles.settingLabel}>{t('settings.termsOfService')}</Text>
            <Text style={styles.chevron}>›</Text>
          </TouchableOpacity>
          <View style={styles.divider} />
          <TouchableOpacity style={styles.settingRow}>
            <Text style={styles.settingLabel}>{t('settings.privacyPolicy')}</Text>
            <Text style={styles.chevron}>›</Text>
          </TouchableOpacity>
        </Card>

        {/* About Section */}
        <Text style={styles.sectionTitle}>{t('settings.about')}</Text>
        <Card style={styles.section}>
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>{t('settings.version')}</Text>
            <Text style={styles.settingValue}>1.0.0</Text>
          </View>
        </Card>

        {/* Logout Button */}
        {isAuthenticated && (
          <Button
            testID="settings_button_logout"
            title={t('auth.logout')}
            onPress={handleLogout}
            variant="outline"
            size="large"
            style={styles.logoutButton}
          />
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1a365d',
    marginBottom: 24,
  },
  profileCard: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#1a365d',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  avatarText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
  },
  profileInfo: {
    flex: 1,
  },
  profileName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
  },
  profileEmail: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 2,
  },
  guestText: {
    fontSize: 16,
    color: '#64748b',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748b',
    marginBottom: 8,
    marginTop: 8,
    textTransform: 'uppercase',
  },
  section: {
    marginBottom: 16,
    padding: 0,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  settingLabel: {
    fontSize: 16,
    color: '#1e293b',
  },
  settingValue: {
    fontSize: 16,
    color: '#64748b',
  },
  chevron: {
    fontSize: 20,
    color: '#94a3b8',
  },
  divider: {
    height: 1,
    backgroundColor: '#e2e8f0',
    marginHorizontal: 16,
  },
  languageList: {
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  languageOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingLeft: 32,
  },
  languageOptionActive: {
    backgroundColor: '#f0f9ff',
  },
  languageText: {
    fontSize: 16,
    color: '#64748b',
  },
  languageTextActive: {
    color: '#1a365d',
    fontWeight: '600',
  },
  logoutButton: {
    marginTop: 24,
    marginBottom: 48,
  },
});
