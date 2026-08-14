// app/lib/core/utils/router.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/learner_flows.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/home',
    routes: [
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
      GoRoute(
        path: '/exercise/:exerciseId',
        builder: (c, s) => ExerciseScreen(exerciseId: s.pathParameters['exerciseId'] ?? 'ex_1'),
      ),
      GoRoute(path: '/repair', builder: (c, s) => const RepairScreen()),
      GoRoute(path: '/review', builder: (c, s) => const ReviewScreen()),
      GoRoute(path: '/progress', builder: (c, s) => const ProgressScreen()),
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
