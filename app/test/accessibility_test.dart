// app/test/accessibility_test.dart

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_lang_pro/core/utils/accessibility_helpers.dart';
import 'package:learning_lang_pro/features/learner_flows.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  group('Accessibility & Responsive Unit & Widget Tests', () {
    testWidgets('AccessibleTouchTarget enforces minimum 48x48 dp touch dimensions', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AccessibleTouchTarget(
              label: 'Test Button',
              onTap: () {},
              child: const Icon(Icons.add, size: 16),
            ),
          ),
        ),
      );

      final Size buttonSize = tester.getSize(find.byType(AccessibleTouchTarget));
      expect(buttonSize.width, greaterThanOrEqualTo(48.0));
      expect(buttonSize.height, greaterThanOrEqualTo(48.0));
    });

    testWidgets('ResponsiveLayoutBuilder adapts grid columns on tablet/web viewports', (WidgetTester tester) async {
      // 1. Mobile viewport (360 x 640)
      tester.view.physicalSize = const Size(360, 640);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      bool isTabletMobile = false;
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveLayoutBuilder(
            builder: (context, isTablet) {
              isTabletMobile = isTablet;
              return Container();
            },
          ),
        ),
      );
      expect(isTabletMobile, isFalse);

      // 2. Tablet viewport (800 x 1200)
      tester.view.physicalSize = const Size(800, 1200);
      bool isTabletTablet = false;
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveLayoutBuilder(
            builder: (context, isTablet) {
              isTabletTablet = isTablet;
              return Container();
            },
          ),
        ),
      );
      expect(isTabletTablet, isTrue);
    });

    testWidgets('ListeningPracticeScreen provides accessible audio control semantics', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: ListeningPracticeScreen(),
          ),
        ),
      );

      expect(find.byType(Semantics), findsWidgets);
      expect(find.byType(AccessibleTouchTarget), findsOneWidget);
    });
  });
}
