// lib/core/utils/router.dart

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../features/auth/screens/splash_screen.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/home/language_selection_screen.dart';
import '../../features/home/level_selection_screen.dart';
import '../../features/grammar/screens/grammar_list_screen.dart';
import '../../features/grammar/screens/grammar_detail_screen.dart';
import '../../features/vocabulary/screens/vocabulary_list_screen.dart';
import '../../features/flashcards/screens/flashcard_screen.dart';
import '../../features/exercises/screens/exercise_hub_screen.dart';
import '../../features/exercises/screens/multiple_choice_screen.dart';
import '../../features/exercises/screens/fill_blank_screen.dart';
import '../../features/exercises/screens/sentence_order_screen.dart';
import '../../features/exercises/screens/translation_screen.dart';
import '../../features/exercises/screens/error_correction_screen.dart';
import '../../features/exercises/screens/exam_screen.dart';
import '../../features/progress/screens/progress_screen.dart';
import '../../features/admin/screens/admin_dashboard_screen.dart';

// ── Route names ────────────────────────────────────────────
class AppRoutes {
  static const splash          = '/';
  static const login           = '/login';
  static const register        = '/register';
  static const languageSelect  = '/languages';
  static const levelSelect     = '/levels/:languageId';
  static const grammarList     = '/grammar/:languageId/:levelId';
  static const grammarDetail   = '/grammar/:languageId/:levelId/:topicId';
  static const vocabularyList  = '/vocabulary/:languageId/:levelId';
  static const flashcards      = '/flashcards/:languageId/:levelId';
  static const exerciseHub     = '/exercises/:languageId/:levelId';
  static const multipleChoice  = '/exercises/mc/:languageId/:levelId';
  static const fillBlank       = '/exercises/fb/:languageId/:levelId';
  static const sentenceOrder   = '/exercises/so/:languageId/:levelId';
  static const translation     = '/exercises/tr/:languageId/:levelId';
  static const errorCorrection = '/exercises/ec/:languageId/:levelId';
  static const exam            = '/exercises/exam/:languageId/:levelId';
  static const progress        = '/progress/:languageId/:levelId';
  static const adminDashboard  = '/admin';
}

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: AppRoutes.splash,
    redirect: (context, state) {
      final isLoggedIn = Supabase.instance.client.auth.currentUser != null;
      final isAuthRoute = state.matchedLocation == AppRoutes.login ||
          state.matchedLocation == AppRoutes.register ||
          state.matchedLocation == AppRoutes.splash;

      if (!isLoggedIn && !isAuthRoute) return AppRoutes.login;
      return null;
    },
    routes: [
      GoRoute(path: AppRoutes.splash,         builder: (c, s) => const SplashScreen()),
      GoRoute(path: AppRoutes.login,          builder: (c, s) => const LoginScreen()),
      GoRoute(path: AppRoutes.register,       builder: (c, s) => const RegisterScreen()),
      GoRoute(path: AppRoutes.languageSelect, builder: (c, s) => const LanguageSelectionScreen()),
      GoRoute(
        path: AppRoutes.levelSelect,
        builder: (c, s) => LevelSelectionScreen(languageId: s.pathParameters['languageId']!),
      ),
      GoRoute(
        path: AppRoutes.grammarList,
        builder: (c, s) => GrammarListScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
        ),
      ),
      GoRoute(
        path: AppRoutes.grammarDetail,
        builder: (c, s) => GrammarDetailScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
          topicId: s.pathParameters['topicId']!,
        ),
      ),
      GoRoute(
        path: AppRoutes.vocabularyList,
        builder: (c, s) => VocabularyListScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
        ),
      ),
      GoRoute(
        path: AppRoutes.flashcards,
        builder: (c, s) => FlashcardScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
        ),
      ),
      GoRoute(
        path: AppRoutes.exerciseHub,
        builder: (c, s) => ExerciseHubScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
        ),
      ),
      GoRoute(
        path: AppRoutes.multipleChoice,
        builder: (c, s) => MultipleChoiceScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
          topicId: s.uri.queryParameters['topicId'],
        ),
      ),
      GoRoute(
        path: AppRoutes.fillBlank,
        builder: (c, s) => FillBlankScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
          topicId: s.uri.queryParameters['topicId'],
        ),
      ),
      GoRoute(
        path: AppRoutes.sentenceOrder,
        builder: (c, s) => SentenceOrderScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
        ),
      ),
      GoRoute(
        path: AppRoutes.translation,
        builder: (c, s) => TranslationScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
        ),
      ),
      GoRoute(
        path: AppRoutes.errorCorrection,
        builder: (c, s) => ErrorCorrectionScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
        ),
      ),
      GoRoute(
        path: AppRoutes.exam,
        builder: (c, s) => ExamScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
        ),
      ),
      GoRoute(
        path: AppRoutes.progress,
        builder: (c, s) => ProgressScreen(
          languageId: s.pathParameters['languageId']!,
          levelId: s.pathParameters['levelId']!,
        ),
      ),
      GoRoute(path: AppRoutes.adminDashboard, builder: (c, s) => const AdminDashboardScreen()),
    ],
  );
});
