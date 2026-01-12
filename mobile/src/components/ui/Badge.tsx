import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';

interface BadgeProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'premium';
  size?: 'small' | 'medium';
  style?: ViewStyle;
  testID?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  label,
  variant = 'primary',
  size = 'medium',
  style,
  testID,
}) => {
  return (
    <View testID={testID} style={[styles.badge, styles[variant], styles[size], style]}>
      <Text style={[styles.text, styles[`${variant}Text`], styles[`${size}Text`]]}>
        {label}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
  // Variants
  primary: {
    backgroundColor: '#e0f2fe',
  },
  secondary: {
    backgroundColor: '#f1f5f9',
  },
  success: {
    backgroundColor: '#dcfce7',
  },
  warning: {
    backgroundColor: '#fef3c7',
  },
  premium: {
    backgroundColor: '#fef3c7',
    borderWidth: 1,
    borderColor: '#f59e0b',
  },
  // Sizes
  small: {
    paddingVertical: 2,
    paddingHorizontal: 8,
  },
  medium: {
    paddingVertical: 4,
    paddingHorizontal: 12,
  },
  // Text
  text: {
    fontWeight: '600',
  },
  primaryText: {
    color: '#0369a1',
  },
  secondaryText: {
    color: '#475569',
  },
  successText: {
    color: '#16a34a',
  },
  warningText: {
    color: '#d97706',
  },
  premiumText: {
    color: '#b45309',
  },
  smallText: {
    fontSize: 10,
  },
  mediumText: {
    fontSize: 12,
  },
});
