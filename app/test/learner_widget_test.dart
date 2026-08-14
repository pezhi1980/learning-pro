// app/test/learner_widget_test.dart

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:learning_lang_pro/features/learner_flows.dart';

void main() {
  group('Learner Widget Tests', () {
    testWidgets('HomeScreen renders streak, XP, and practice cards', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: HomeScreen(),
          ),
        ),
      );

      expect(find.textContaining('Welcome,'), findsOneWidget);
      expect(find.text('Streak'), findsOneWidget);
      expect(find.text('XP'), findsOneWidget);
      expect(find.text('DAILY PRACTICE'), findsOneWidget);
    });

    testWidgets('ContinueLearningScreen renders resume button', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: ContinueLearningScreen(),
          ),
        ),
      );

      expect(find.text('Continue Learning'), findsOneWidget);
      expect(find.text('Resume Active Micro-Lesson'), findsOneWidget);
    });
  });
}
