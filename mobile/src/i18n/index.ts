import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as Localization from 'expo-localization';

import en from './locales/en.json';
import hr from './locales/hr.json';
import de from './locales/de.json';

const resources = {
  en: { translation: en },
  hr: { translation: hr },
  de: { translation: de },
};

// Get device language or default to 'en'
const getDeviceLanguage = (): string => {
  const locale = Localization.locale.split('-')[0];
  return ['en', 'hr', 'de'].includes(locale) ? locale : 'en';
};

i18n.use(initReactI18next).init({
  resources,
  lng: getDeviceLanguage(),
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
  compatibilityJSON: 'v3',
});

export default i18n;
