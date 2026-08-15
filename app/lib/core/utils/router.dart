// app/lib/core/utils/router.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/screens/splash_screen.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/home/language_selection_screen.dart';
import '../../features/home/category_selection_screen.dart';
import '../../features/home/level_selection_screen.dart';
import '../../features/grammar/screens/grammar_list_screen.dart';
import '../../features/grammar/screens/grammar_detail_screen.dart';
import '../../features/vocabulary/screens/vocabulary_list_screen.dart';
import '../../features/exercises/screens/multiple_choice_screen.dart';
import '../../features/progress/screens/progress_screen.dart';
import '../../features/learner_flows.dart' hide ProgressScreen;

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String languageSelect = '/language-select';
  static const String categorySelect = '/category-select/:langId';
  static const String levels = '/levels/:langId';
  static const String grammarList = '/grammar/:langId/:levelId';
  static const String grammarDetail = '/grammar-detail/:langId/:levelId/:topicId';
  static const String vocabularyList = '/vocabulary/:langId/:levelId';
  static const String exerciseMC = '/exercises/:langId/:levelId';
  static const String progress = '/progress';
  static const String home = '/home';
}

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (c, s) => const SplashScreen()),
      GoRoute(path: '/login', builder: (c, s) => const LoginScreen()),
      GoRoute(path: '/register', builder: (c, s) => const RegisterScreen()),
      GoRoute(path: '/language-select', builder: (c, s) => const LanguageSelectionScreen()),
      GoRoute(
        path: '/category-select/:langId',
        builder: (c, s) => CategorySelectionScreen(
          languageId: s.pathParameters['langId'] ?? 'en',
        ),
      ),
      GoRoute(
        path: '/levels/:langId',
        builder: (c, s) => LevelSelectionScreen(
          languageId: s.pathParameters['langId'] ?? 'en',
        ),
      ),
      GoRoute(
        path: '/grammar/:langId/:levelId',
        builder: (c, s) => GrammarListScreen(
          languageId: s.pathParameters['langId'] ?? 'en',
          levelId: s.pathParameters['levelId'] ?? 'A1',
        ),
      ),
      GoRoute(
        path: '/grammar/:langId/:levelId/:topicId',
        builder: (c, s) => GrammarDetailScreen(
          languageId: s.pathParameters['langId'] ?? 'en',
          levelId: s.pathParameters['levelId'] ?? 'A1',
          topicId: s.pathParameters['topicId'] ?? '',
        ),
      ),
      GoRoute(
        path: '/grammar-detail/:langId/:levelId/:topicId',
        builder: (c, s) => GrammarDetailScreen(
          languageId: s.pathParameters['langId'] ?? 'en',
          levelId: s.pathParameters['levelId'] ?? 'A1',
          topicId: s.pathParameters['topicId'] ?? '',
        ),
      ),
      GoRoute(
        path: '/vocabulary/:langId/:levelId',
        builder: (c, s) => VocabularyListScreen(
          languageId: s.pathParameters['langId'] ?? 'en',
          levelId: s.pathParameters['levelId'] ?? 'A1',
        ),
      ),
      GoRoute(
        path: '/exercises/:langId/:levelId',
        builder: (c, s) => MultipleChoiceScreen(
          languageId: s.pathParameters['langId'] ?? 'en',
          levelId: s.pathParameters['levelId'] ?? 'A1',
          topicId: s.uri.queryParameters['topicId'],
        ),
      ),
      GoRoute(
        path: '/exercises/mc/:langId/:levelId',
        builder: (c, s) => MultipleChoiceScreen(
          languageId: s.pathParameters['langId'] ?? 'en',
          levelId: s.pathParameters['levelId'] ?? 'A1',
          topicId: s.uri.queryParameters['topicId'],
        ),
      ),
      GoRoute(
        path: '/exercise-mc/:langId/:levelId/:topicId',
        builder: (c, s) => MultipleChoiceScreen(
          languageId: s.pathParameters['langId'] ?? 'en',
          levelId: s.pathParameters['levelId'] ?? 'A1',
          topicId: s.pathParameters['topicId'],
        ),
      ),
      GoRoute(
        path: '/exercise/:exerciseId',
        builder: (c, s) => MultipleChoiceScreen(
          languageId: 'en',
          levelId: 'A1',
          topicId: s.pathParameters['exerciseId'],
        ),
      ),
      GoRoute(
        path: '/progress',
        builder: (c, s) => ProgressScreen(
          languageId: s.uri.queryParameters['langId'] ?? 'en',
          levelId: s.uri.queryParameters['levelId'] ?? 'A1',
        ),
      ),

      // Learner flow fallback routes
      GoRoute(path: '/home', builder: (c, s) => const HomeScreen()),
      GoRoute(path: '/continue-learning', builder: (c, s) => const ContinueLearningScreen()),
      GoRoute(path: '/course', builder: (c, s) => const CourseScreen()),
      GoRoute(
        path: '/level/:level',
        builder: (c, s) => LevelScreen(level: s.pathParameters['level'] ?? 'A1'),
      ),
      GoRoute(
        path: '/unit/:unitId',
        builder: (c, s) => UnitScreen(unitId: s.pathParameters['unitId'] ?? 'unit:A1:1'),
      ),
      GoRoute(
        path: '/topic/:topicId',
        builder: (c, s) => TopicScreen(topicId: s.pathParameters['topicId'] ?? 'topic:1'),
      ),
      GoRoute(
        path: '/micro-lesson/:mlId',
        builder: (c, s) => MicroLessonScreen(mlId: s.pathParameters['mlId'] ?? 'ml:1'),
      ),
      GoRoute(path: '/daily-session', builder: (c, s) => const DailySessionScreen()),
      GoRoute(
        path: '/grammar-lesson/:code',
        builder: (c, s) => GrammarLessonScreen(grammarCode: s.pathParameters['code'] ?? 'g_present_simple'),
      ),
      GoRoute(
        path: '/vocabulary-lesson/:lexeme',
        builder: (c, s) => VocabularyLessonScreen(lexeme: s.pathParameters['lexeme'] ?? 'apple'),
      ),
      GoRoute(path: '/repair', builder: (c, s) => const RepairScreen()),
      GoRoute(path: '/review', builder: (c, s) => const ReviewScreen()),
      GoRoute(path: '/placement', builder: (c, s) => const PlacementTestScreen()),
      GoRoute(path: '/diagnostic', builder: (c, s) => const DiagnosticAssessmentScreen()),
      GoRoute(path: '/checkpoint', builder: (c, s) => const CheckpointTestScreen()),
      GoRoute(path: '/level-assessment', builder: (c, s) => const LevelAssessmentScreen()),
      GoRoute(path: '/listening', builder: (c, s) => const ListeningPracticeScreen()),
      GoRoute(path: '/speaking', builder: (c, s) => const SpeakingPracticeScreen()),
      GoRoute(path: '/writing', builder: (c, s) => const WritingPracticeScreen()),
      GoRoute(path: '/search', builder: (c, s) => const SearchScreen()),
      GoRoute(path: '/bookmarks', builder: (c, s) => const BookmarksScreen()),
      GoRoute(path: '/history', builder: (c, s) => const HistoryScreen()),
      GoRoute(path: '/settings', builder: (c, s) => const SettingsScreen()),
    ],
  );
});


