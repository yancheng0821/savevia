import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import en from './locales/en.json'
import zh from './locales/zh.json'
import fr from './locales/fr.json'
import es from './locales/es.json'
import ko from './locales/ko.json'
import ja from './locales/ja.json'

const resources = {
  en: { translation: en },
  zh: { translation: zh },
  fr: { translation: fr },
  es: { translation: es },
  ko: { translation: ko },
  ja: { translation: ja },
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    supportedLngs: ['en', 'zh', 'fr', 'es', 'ko', 'ja'],
    nonExplicitSupportedLngs: true, // Allow zh-CN, zh-TW to match zh
    load: 'languageOnly', // Only load 'zh' instead of 'zh-CN'
    debug: false,
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'language',
    },
  })

export default i18n
