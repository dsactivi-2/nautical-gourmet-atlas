import React from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '../../src/components/ui';

export default function WelcomeScreen() {
  const router = useRouter();
  const { t } = useTranslation();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Text style={styles.logo}>⚓</Text>
          <Text style={styles.title}>Nautical{'\n'}Gourmet Atlas</Text>
        </View>

        <Text style={styles.subtitle}>{t('auth.welcome')}</Text>
      </View>

      <View style={styles.buttons}>
        <Button
          testID="welcome_button_login"
          title={t('auth.login')}
          onPress={() => router.push('/(auth)/login')}
          variant="primary"
          size="large"
          style={styles.button}
        />
        <Button
          testID="welcome_button_register"
          title={t('auth.register')}
          onPress={() => router.push('/(auth)/register')}
          variant="outline"
          size="large"
          style={styles.button}
        />
        <Button
          testID="welcome_button_guest"
          title={t('auth.continueAsGuest')}
          onPress={() => router.replace('/(tabs)/map')}
          variant="ghost"
          size="medium"
          style={styles.guestButton}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
    padding: 24,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logo: {
    fontSize: 80,
    marginBottom: 16,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1a365d',
    textAlign: 'center',
    lineHeight: 40,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
    lineHeight: 24,
  },
  buttons: {
    gap: 12,
  },
  button: {
    width: '100%',
  },
  guestButton: {
    marginTop: 8,
  },
});
