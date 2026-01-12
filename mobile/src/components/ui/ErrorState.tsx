import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTranslation } from 'react-i18next';
import { Button } from './Button';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ message, onRetry }) => {
  const { t } = useTranslation();

  return (
    <View style={styles.container} testID="error_state">
      <Text style={styles.emoji}>😕</Text>
      <Text style={styles.message}>{message || t('common.error')}</Text>
      {onRetry && (
        <Button
          title={t('common.retry')}
          onPress={onRetry}
          variant="outline"
          style={styles.button}
          testID="error_state_retry_button"
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emoji: {
    fontSize: 48,
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
    lineHeight: 24,
  },
  button: {
    marginTop: 24,
  },
});
