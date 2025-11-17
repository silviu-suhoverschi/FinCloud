import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import ro from './locales/ro.json';
import { mmkvStorage, StorageKeys } from '../storage/mmkv';

const resources = {
  en: { translation: en },
  ro: { translation: ro },
};

// Get saved language or default to English
const savedLanguage = mmkvStorage.getString(StorageKeys.LANGUAGE) || 'en';

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: savedLanguage,
    fallbackLng: 'en',
    compatibilityJSON: 'v3',
    interpolation: {
      escapeValue: false,
    },
  });

/**
 * Change app language
 */
export const changeLanguage = (language: 'en' | 'ro') => {
  i18n.changeLanguage(language);
  mmkvStorage.set(StorageKeys.LANGUAGE, language);
};

/**
 * Get current language
 */
export const getCurrentLanguage = (): 'en' | 'ro' => {
  return (i18n.language as 'en' | 'ro') || 'en';
};

export default i18n;
