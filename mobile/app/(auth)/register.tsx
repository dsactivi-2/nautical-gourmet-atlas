import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  TouchableOpacity,
  Switch,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useForm, Controller } from 'react-hook-form';
import { Button, Input } from '../../src/components/ui';
import { useAuthStore } from '../../src/hooks/useAuthStore';
import { getApiError } from '../../src/api';
import type { UserCreate } from '../../src/types';

export default function RegisterScreen() {
  const router = useRouter();
  const { t } = useTranslation();
  const register = useAuthStore((state) => state.register);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<UserCreate>({
    defaultValues: {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      is_nautical: false,
    },
  });

  const onSubmit = async (data: UserCreate) => {
    setIsLoading(true);
    try {
      await register(data);
      router.replace('/(tabs)/map');
    } catch (error) {
      const apiError = getApiError(error);
      Alert.alert('Error', apiError.detail);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Text style={styles.backText}>← {t('common.back')}</Text>
          </TouchableOpacity>

          <Text style={styles.title}>{t('auth.register')}</Text>
          <Text style={styles.subtitle}>{t('auth.welcome')}</Text>

          <View style={styles.form}>
            <View style={styles.row}>
              <View style={styles.halfInput}>
                <Controller
                  control={control}
                  name="first_name"
                  rules={{ required: 'First name is required' }}
                  render={({ field: { onChange, onBlur, value } }) => (
                    <Input
                      testID="register_input_firstName"
                      label={t('auth.firstName')}
                      placeholder="John"
                      value={value}
                      onChangeText={onChange}
                      onBlur={onBlur}
                      error={errors.first_name?.message}
                    />
                  )}
                />
              </View>
              <View style={styles.halfInput}>
                <Controller
                  control={control}
                  name="last_name"
                  rules={{ required: 'Last name is required' }}
                  render={({ field: { onChange, onBlur, value } }) => (
                    <Input
                      testID="register_input_lastName"
                      label={t('auth.lastName')}
                      placeholder="Doe"
                      value={value}
                      onChangeText={onChange}
                      onBlur={onBlur}
                      error={errors.last_name?.message}
                    />
                  )}
                />
              </View>
            </View>

            <Controller
              control={control}
              name="email"
              rules={{
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address',
                },
              }}
              render={({ field: { onChange, onBlur, value } }) => (
                <Input
                  testID="register_input_email"
                  label={t('auth.email')}
                  placeholder="your@email.com"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  error={errors.email?.message}
                />
              )}
            />

            <Controller
              control={control}
              name="password"
              rules={{
                required: 'Password is required',
                minLength: {
                  value: 6,
                  message: 'Password must be at least 6 characters',
                },
              }}
              render={({ field: { onChange, onBlur, value } }) => (
                <Input
                  testID="register_input_password"
                  label={t('auth.password')}
                  placeholder="••••••••"
                  secureTextEntry={!showPassword}
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                  error={errors.password?.message}
                  rightIcon={<Text>{showPassword ? '👁' : '👁‍🗨'}</Text>}
                  onRightIconPress={() => setShowPassword(!showPassword)}
                />
              )}
            />

            <Controller
              control={control}
              name="is_nautical"
              render={({ field: { onChange, value } }) => (
                <View style={styles.switchRow}>
                  <Text style={styles.switchLabel}>{t('auth.isNautical')}</Text>
                  <Switch
                    testID="register_switch_nautical"
                    value={value}
                    onValueChange={onChange}
                    trackColor={{ false: '#e2e8f0', true: '#1a365d' }}
                    thumbColor="#fff"
                  />
                </View>
              )}
            />

            <Button
              testID="register_button_submit"
              title={t('auth.register')}
              onPress={handleSubmit(onSubmit)}
              loading={isLoading}
              size="large"
              style={styles.submitButton}
            />

            <View style={styles.footer}>
              <Text style={styles.footerText}>{t('auth.haveAccount')}</Text>
              <TouchableOpacity onPress={() => router.push('/(auth)/login')}>
                <Text style={styles.link}>{t('auth.login')}</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
  },
  backButton: {
    marginBottom: 32,
  },
  backText: {
    fontSize: 16,
    color: '#1a365d',
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1a365d',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    marginBottom: 32,
  },
  form: {
    flex: 1,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  halfInput: {
    flex: 1,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    marginBottom: 16,
  },
  switchLabel: {
    fontSize: 14,
    color: '#1e293b',
    flex: 1,
  },
  submitButton: {
    marginTop: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
    gap: 8,
  },
  footerText: {
    fontSize: 14,
    color: '#64748b',
  },
  link: {
    fontSize: 14,
    color: '#1a365d',
    fontWeight: '600',
  },
});
