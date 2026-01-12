import { Tabs } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { Text, StyleSheet } from 'react-native';

export default function TabsLayout() {
  const { t } = useTranslation();

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarActiveTintColor: '#1a365d',
        tabBarInactiveTintColor: '#94a3b8',
        tabBarLabelStyle: styles.tabBarLabel,
      }}
    >
      <Tabs.Screen
        name="map"
        options={{
          title: t('tabs.map'),
          tabBarIcon: ({ color }) => <Text style={[styles.icon, { color }]}>🗺</Text>,
        }}
      />
      <Tabs.Screen
        name="favorites"
        options={{
          title: t('tabs.favorites'),
          tabBarIcon: ({ color }) => <Text style={[styles.icon, { color }]}>❤️</Text>,
        }}
      />
      <Tabs.Screen
        name="treasures"
        options={{
          title: t('tabs.treasures'),
          tabBarIcon: ({ color }) => <Text style={[styles.icon, { color }]}>💎</Text>,
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: t('tabs.settings'),
          tabBarIcon: ({ color }) => <Text style={[styles.icon, { color }]}>⚙️</Text>,
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
    paddingTop: 8,
    paddingBottom: 8,
    height: 80,
  },
  tabBarLabel: {
    fontSize: 12,
    fontWeight: '500',
  },
  icon: {
    fontSize: 24,
  },
});
