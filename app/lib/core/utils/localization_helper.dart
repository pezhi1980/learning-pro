// lib/core/utils/localization_helper.dart

import 'dart:ui' as ui;
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/app_constants.dart';

class LocalizationHelper {
  LocalizationHelper._();

  static const Map<String, String> nativeLanguageNames = {
    'en': 'English',
    'da': 'Dansk',
    'fa': 'فارسی (Persian)',
    'de': 'Deutsch',
    'fr': 'Français',
    'es': 'Español',
    'ar': 'العربية (Arabic)',
  };

  static const Map<String, String> nativeLanguageFlags = {
    'en': '🇬🇧',
    'da': '🇩🇰',
    'fa': '🇮🇷',
    'de': '🇩🇪',
    'fr': '🇫🇷',
    'es': '🇪🇸',
    'ar': '🇸🇦',
  };

  /// Detect device system language or fallback to English
  static String getDeviceLanguageCode() {
    final systemLocale = ui.PlatformDispatcher.instance.locale.languageCode.toLowerCase();
    if (nativeLanguageNames.containsKey(systemLocale)) {
      return systemLocale;
    }
    return 'en';
  }

  /// Get current user's preferred explanation language
  static Future<String> getSelectedExplanationLanguage() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString(AppConstants.keyNativeLanguage);
    if (saved != null && saved.isNotEmpty) {
      return saved;
    }
    // Default to device locale if available, else 'en'
    final deviceLang = getDeviceLanguageCode();
    await prefs.setString(AppConstants.keyNativeLanguage, deviceLang);
    return deviceLang;
  }

  /// Set user's preferred explanation language
  static Future<void> setSelectedExplanationLanguage(String langCode) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyNativeLanguage, langCode);
  }

  /// Basic UI translations for standard navigation strings
  static String tr(String key, {String lang = 'en'}) {
    final translations = _strings[lang] ?? _strings['en']!;
    return translations[key] ?? _strings['en']?[key] ?? key;
  }

  static const Map<String, Map<String, String>> _strings = {
    'en': {
      'your_choice': 'Choose Your Focus ✨',
      'choose_section': 'What would you like to practice? Grammar or Vocabulary?',
      'grammar_title': 'Grammar',
      'grammar_desc': 'Structured grammar lessons from A1 to C2 with rules, contrasts, and real examples.',
      'vocab_title': 'Vocabulary',
      'vocab_desc': 'Essential vocabulary, words by CEFR level, definitions, and flashcards.',
      'grammar_badge': 'A1 - C2 Lessons',
      'vocab_badge': 'Words & Cards',
      'enter_section': 'Enter Section',
      'explanation_language': 'Explanation Language',
      'change_language': 'Change',
    },
    'da': {
      'your_choice': 'Vælg dit fokus ✨',
      'choose_section': 'Hvad vil du gerne øve? Grammatik eller ordforråd?',
      'grammar_title': 'Grammatik (Grammar)',
      'grammar_desc': 'Strukturerede grammatiklektioner fra A1 til C2 med forklaringer og eksempler.',
      'vocab_title': 'Ordforråd (Vocabulary)',
      'vocab_desc': 'Vigtige ord efter CEFR-niveau, udtale, definitioner og flashcards.',
      'grammar_badge': 'A1 - C2 Lektioner',
      'vocab_badge': 'Ord & Kort',
      'enter_section': 'Gå til sektion',
      'explanation_language': 'Forklaringssprog',
      'change_language': 'Skift',
    },
    'fa': {
      'your_choice': 'حق انتخاب شما ✨',
      'choose_section': 'چه بخشی را می‌خواهید شروع کنید؟ گرامر یا لغات؟',
      'grammar_title': 'گرامر (Grammar)',
      'grammar_desc': 'آموزش گرامر از سطح A1 تا C2 همراه با توضیح تفاوت‌ها و مثال‌های کاربردی.',
      'vocab_title': 'لغات (Vocabulary)',
      'vocab_desc': 'آموزش و مرور لغات کاربردی، اصطلاحات و کلمات سطح‌بندی شده.',
      'grammar_badge': 'سطوح A1 تا C2',
      'vocab_badge': 'کلمات و فلش‌کارت',
      'enter_section': 'ورود به این بخش',
      'explanation_language': 'زبان توضیحات درس',
      'change_language': 'تغییر',
    },
    'de': {
      'your_choice': 'Wähle deinen Schwerpunkt ✨',
      'choose_section': 'Was möchtest du üben? Grammatik oder Wortschatz?',
      'grammar_title': 'Grammatik (Grammar)',
      'grammar_desc': 'Strukturierte Grammatiklektionen von A1 bis C2 mit Beispielen.',
      'vocab_title': 'Wortschatz (Vocabulary)',
      'vocab_desc': 'Wichtige Vokabeln nach CEFR-Niveau und Karteikarten.',
      'grammar_badge': 'A1 - C2 Lektionen',
      'vocab_badge': 'Wörter & Karten',
      'enter_section': 'Bereich betreten',
      'explanation_language': 'Erklärungssprache',
      'change_language': 'Ändern',
    },
    'fr': {
      'your_choice': 'Choisissez votre parcours ✨',
      'choose_section': 'Que voulez-vous pratiquer ? Grammaire ou Vocabulaire ?',
      'grammar_title': 'Grammaire (Grammar)',
      'grammar_desc': 'Leçons de grammaire structurées du A1 au C2 avec règles et exemples.',
      'vocab_title': 'Vocabulaire (Vocabulary)',
      'vocab_desc': 'Vocabulaire essentiel par niveau CECRL et cartes mémoire.',
      'grammar_badge': 'Leçons A1 - C2',
      'vocab_badge': 'Mots & Cartes',
      'enter_section': 'Accéder',
      'explanation_language': 'Langue des explications',
      'change_language': 'Changer',
    },
    'es': {
      'your_choice': 'Elige tu enfoque ✨',
      'choose_section': '¿Qué te gustaría practicar? ¿Gramática o Vocabulario?',
      'grammar_title': 'Gramática (Grammar)',
      'grammar_desc': 'Lecciones de gramática estructuradas de A1 a C2 con reglas y ejemplos.',
      'vocab_title': 'Vocabulario (Vocabulary)',
      'vocab_desc': 'Vocabulario esencial por nivel MCER y tarjetas didácticas.',
      'grammar_badge': 'Lecciones A1 - C2',
      'vocab_badge': 'Palabras y Tarjetas',
      'enter_section': 'Entrar a la sección',
      'explanation_language': 'Idioma de explicación',
      'change_language': 'Cambiar',
    },
  };
}
