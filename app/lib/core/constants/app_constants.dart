// lib/core/constants/app_constants.dart

class AppConstants {
  AppConstants._();

  // App Info
  static const String appName = 'Learning Lang Pro';
  static const String appVersion = '1.0.0';

  // Supported target languages (languages the user can LEARN)
  static const List<String> targetLanguages = ['en'];
  // Will grow: ['en', 'fr', 'de', 'it', 'es']

  // Supported native languages (user's mother tongue for explanations)
  static const List<String> nativeLanguages = ['fa', 'en'];
  // Will grow: ['fa', 'en', 'ar', 'fr', 'de', 'it', 'es']

  // RTL languages
  static const List<String> rtlLanguages = ['fa', 'ar'];

  // CEFR Levels
  static const List<String> levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

  // Flashcard levels (A1–B1)
  static const List<String> flashcardLevels = ['A1', 'A2', 'B1'];

  // Grammar contrast levels (A1–B2)
  static const List<String> grammarContrastLevels = ['A1', 'A2', 'B1', 'B2'];

  // Exercise settings
  static const int questionsPerSet = 5;

  // Storage keys
  static const String keyNativeLanguage = 'native_language';
  static const String keyLastSelectedLanguage = 'last_language';
  static const String keyLastSelectedLevel = 'last_level';
  static const String keyOnboardingDone = 'onboarding_done';

  // API timeouts
  static const Duration apiTimeout = Duration(seconds: 30);

  // Animation durations
  static const Duration animFast = Duration(milliseconds: 200);
  static const Duration animNormal = Duration(milliseconds: 350);
  static const Duration animSlow = Duration(milliseconds: 600);
}
