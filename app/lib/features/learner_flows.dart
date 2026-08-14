// app/lib/features/learner_flows.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/providers/app_providers.dart';
import '../core/theme/app_theme.dart';
import '../core/utils/accessibility_helpers.dart';

// ── 1. HOME SCREEN ─────────────────────────────────────────────────────────

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);

    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(
        title: Text('Welcome, ${auth.displayName}'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          Semantics(
            label: 'Saved Bookmarks',
            hint: 'Tap to view saved lessons and targets',
            button: true,
            child: AccessibleTouchTarget(
              onTap: () => context.push('/bookmarks'),
              child: const Icon(Icons.bookmark_border),
            ),
          ),
          Semantics(
            label: 'User Settings',
            hint: 'Tap to open settings and accessibility preferences',
            button: true,
            child: AccessibleTouchTarget(
              onTap: () => context.push('/settings'),
              child: const Icon(Icons.settings),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Daily Streak & XP Bar
            Semantics(
              label: 'Learning Streak and XP Progress',
              value: '5 Days Streak, 350 XP',
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.darkSurface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.primaryColor.withOpacity(0.3)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Row(
                      children: [
                        const ExcludeSemantics(child: Icon(Icons.local_fire_department, color: Colors.orange, size: 28)),
                        const SizedBox(width: 8),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: const [
                            Text('Streak', style: TextStyle(color: Colors.grey, fontSize: 12)),
                            Text('5 Days', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                          ],
                        ),
                      ],
                    ),
                    Row(
                      children: [
                        const ExcludeSemantics(child: Icon(Icons.stars, color: Colors.amber, size: 28)),
                        const SizedBox(width: 8),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: const [
                            Text('XP', style: TextStyle(color: Colors.grey, fontSize: 12)),
                            Text('350 XP', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Continue Learning Daily Session Banner
            Card(
              color: AppTheme.primaryColor,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('DAILY PRACTICE', style: TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Text('${auth.level} Core Daily Session', style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    Semantics(
                      label: 'Start Daily Practice Session',
                      button: true,
                      child: AccessibleTouchTarget(
                        onTap: () => context.push('/daily-session'),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
                          child: Text('Start Practice', style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Quick Navigation Grid (Responsive Layout)
            const Text('Explore Courses & Activities', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),

            ResponsiveLayoutBuilder(
              builder: (context, isTabletOrDesktop) {
                final columns = isTabletOrDesktop ? 4 : 2;
                return GridView.count(
                  crossAxisCount: columns,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                  childAspectRatio: 1.4,
                  children: [
                    _buildNavTile(context, 'Course Map', Icons.map, Colors.blue, '/course'),
                    _buildNavTile(context, 'Review', Icons.replay, Colors.purple, '/review'),
                    _buildNavTile(context, 'Repair', Icons.build, Colors.redAccent, '/repair'),
                    _buildNavTile(context, 'Progress', Icons.bar_chart, Colors.green, '/progress'),
                    _buildNavTile(context, 'Listening', Icons.headphones, Colors.teal, '/listening'),
                    _buildNavTile(context, 'Speaking', Icons.mic, Colors.deepOrange, '/speaking'),
                    _buildNavTile(context, 'Writing', Icons.edit_note, Colors.indigo, '/writing'),
                    _buildNavTile(context, 'Placement Test', Icons.assignment, Colors.amber, '/placement'),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavTile(BuildContext context, String title, IconData icon, Color color, String route) {
    return Semantics(
      label: title,
      button: true,
      child: AccessibleTouchTarget(
        onTap: () => context.push(route),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppTheme.darkSurface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ExcludeSemantics(child: Icon(icon, color: color, size: 32)),
              const SizedBox(height: 8),
              Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
            ],
          ),
        ),
      ),
    );
  }
}

// ── 2. CONTINUE LEARNING SCREEN ───────────────────────────────────────────

class ContinueLearningScreen extends StatelessWidget {
  const ContinueLearningScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Continue Learning'), backgroundColor: Colors.transparent),
      body: Center(
        child: Semantics(
          label: 'Resume Active Micro-Lesson',
          button: true,
          child: AccessibleTouchTarget(
            onTap: () => context.push('/daily-session'),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              decoration: BoxDecoration(color: AppTheme.primaryColor, borderRadius: BorderRadius.circular(12)),
              child: const Text('Resume Active Micro-Lesson', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ),
        ),
      ),
    );
  }
}

// ── 3. COURSE SCREEN ───────────────────────────────────────────────────────

class CourseScreen extends StatelessWidget {
  const CourseScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Course Map (CEFR A1-C2)'), backgroundColor: Colors.transparent),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: levels.length,
        itemBuilder: (context, index) {
          final level = levels[index];
          return Card(
            color: AppTheme.darkSurface,
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: AppTheme.primaryColor,
                child: Text(level, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
              title: Text('CEFR Level $level', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              subtitle: const Text('Authoritative PDF Curriculum', style: TextStyle(color: Colors.grey)),
              trailing: const Icon(Icons.arrow_forward_ios, color: Colors.white54, size: 16),
              onTap: () => context.push('/level/$level'),
            ),
          );
        },
      ),
    );
  }
}

// ── 4. LEVEL SCREEN ────────────────────────────────────────────────────────

class LevelScreen extends StatelessWidget {
  final String level;
  const LevelScreen({super.key, required this.level});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: Text('Level $level Course Units'), backgroundColor: Colors.transparent),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: 5,
        itemBuilder: (context, index) {
          final unitId = 'unit:$level:${index + 1}';
          return Card(
            color: AppTheme.darkSurface,
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              title: Text('$level Unit ${index + 1}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              subtitle: const Text('2 Topics • 4 Micro-Lessons', style: TextStyle(color: Colors.grey)),
              trailing: ElevatedButton(
                onPressed: () => context.push('/unit/$unitId'),
                child: const Text('View Unit'),
              ),
            ),
          );
        },
      ),
    );
  }
}

// ── 5. UNIT SCREEN ─────────────────────────────────────────────────────────

class UnitScreen extends StatelessWidget {
  final String unitId;
  const UnitScreen({super.key, required this.unitId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: Text('Unit View ($unitId)'), backgroundColor: Colors.transparent),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Topics in $unitId', style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                itemCount: 2,
                itemBuilder: (context, idx) {
                  final topicId = '$unitId:topic:${idx + 1}';
                  return Card(
                    color: AppTheme.darkSurface,
                    child: ListTile(
                      title: Text('Topic ${idx + 1}', style: const TextStyle(color: Colors.white)),
                      subtitle: const Text('Grammar & Supporting Vocabulary', style: TextStyle(color: Colors.grey)),
                      onTap: () => context.push('/topic/$topicId'),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── 6. TOPIC SCREEN ────────────────────────────────────────────────────────

class TopicScreen extends StatelessWidget {
  final String topicId;
  const TopicScreen({super.key, required this.topicId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: Text('Topic ($topicId)'), backgroundColor: Colors.transparent),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: 3,
        itemBuilder: (context, idx) {
          final mlId = '$topicId:ml:${idx + 1}';
          return Card(
            color: AppTheme.darkSurface,
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: const Icon(Icons.play_circle_fill, color: Colors.blue),
              title: Text('Micro-Lesson ${idx + 1}', style: const TextStyle(color: Colors.white)),
              onTap: () => context.push('/micro-lesson/$mlId'),
            ),
          );
        },
      ),
    );
  }
}

// ── 7. MICRO LESSON SCREEN ─────────────────────────────────────────────────

class MicroLessonScreen extends StatelessWidget {
  final String mlId;
  const MicroLessonScreen({super.key, required this.mlId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: Text('Micro-Lesson ($mlId)'), backgroundColor: Colors.transparent),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            ElevatedButton(
              onPressed: () => context.push('/grammar-lesson/g_present_simple'),
              child: const Text('Grammar Target Explanation'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: () => context.push('/vocabulary-lesson/v_apple'),
              child: const Text('Supporting Vocabulary Target'),
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: () => context.push('/exercise/ex_ml_101'),
              child: const Text('Start Micro-Lesson Exercises'),
            ),
          ],
        ),
      ),
    );
  }
}

// ── 8. DAILY SESSION SCREEN ────────────────────────────────────────────────

class DailySessionScreen extends ConsumerWidget {
  const DailySessionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Daily Session Runner'), backgroundColor: Colors.transparent),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.school, color: AppTheme.primaryColor, size: 64),
            const SizedBox(height: 16),
            const Text('Executing Daily Session', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.push('/exercise/ex_daily_1'),
              child: const Text('Proceed to Daily Exercises'),
            ),
          ],
        ),
      ),
    );
  }
}

// ── 9. GRAMMAR LESSON SCREEN ───────────────────────────────────────────────

class GrammarLessonScreen extends StatelessWidget {
  final String grammarCode;
  const GrammarLessonScreen({super.key, required this.grammarCode});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: Text('Grammar: $grammarCode'), backgroundColor: Colors.transparent),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Grammar Code: $grammarCode', style: const TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 12),
            const Text('Rule & Structure', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: AppTheme.darkSurface, borderRadius: BorderRadius.circular(12)),
              child: const Text('Subject + Verb (Present Simple pattern). Authorized PDF Curriculum rule.', style: TextStyle(color: Colors.white70)),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.push('/exercise/ex_g_1'),
              child: const Text('Practice Grammar Exercises'),
            ),
          ],
        ),
      ),
    );
  }
}

// ── 10. VOCABULARY LESSON SCREEN ───────────────────────────────────────────

class VocabularyLessonScreen extends StatelessWidget {
  final String lexeme;
  const VocabularyLessonScreen({super.key, required this.lexeme});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: Text('Vocabulary: $lexeme'), backgroundColor: Colors.transparent),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(lexeme, style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
            const Text('Noun • CEFR A1', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 16),
            Semantics(
              label: 'Play Audio Example for $lexeme',
              hint: 'Tap to listen to pronunciation and sentence example',
              button: true,
              child: AccessibleTouchTarget(
                onTap: () {},
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(color: AppTheme.darkSurface, borderRadius: BorderRadius.circular(12)),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: const [
                      Icon(Icons.volume_up, color: Colors.blue),
                      SizedBox(width: 8),
                      Text('Play Audio Example', style: TextStyle(color: Colors.white)),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── 11. EXERCISE SCREEN ────────────────────────────────────────────────────

class ExerciseScreen extends StatefulWidget {
  final String exerciseId;
  const ExerciseScreen({super.key, required this.exerciseId});

  @override
  State<ExerciseScreen> createState() => _ExerciseScreenState();
}

class _ExerciseScreenState extends State<ExerciseScreen> {
  int? selectedOption;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: Text('Exercise (${widget.exerciseId})'), backgroundColor: Colors.transparent),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Select the correct form:', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            const Text('She ___ to school every day.', style: TextStyle(color: Colors.white70, fontSize: 16)),
            const SizedBox(height: 24),
            _buildOption(1, 'goes'),
            _buildOption(2, 'go'),
            _buildOption(3, 'gone'),
            const Spacer(),
            Semantics(
              label: 'Submit Answer',
              button: true,
              enabled: selectedOption != null,
              child: AccessibleTouchTarget(
                onTap: selectedOption == null
                    ? null
                    : () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(selectedOption == 1 ? 'Correct! +10 XP' : 'Incorrect.'),
                            backgroundColor: selectedOption == 1 ? Colors.green : Colors.red,
                          ),
                        );
                      },
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: selectedOption != null ? AppTheme.primaryColor : Colors.grey,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Center(
                    child: Text('Submit Answer', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOption(int index, String text) {
    final isSelected = selectedOption == index;
    return Semantics(
      label: 'Option $index: $text',
      selected: isSelected,
      button: true,
      child: AccessibleTouchTarget(
        onTap: () => setState(() => selectedOption = index),
        child: Card(
          color: isSelected ? AppTheme.primaryColor.withOpacity(0.3) : AppTheme.darkSurface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: isSelected ? AppTheme.primaryColor : Colors.transparent),
          ),
          child: ListTile(
            title: Text(text, style: const TextStyle(color: Colors.white)),
          ),
        ),
      ),
    );
  }
}

// ── 12. REPAIR SCREEN ──────────────────────────────────────────────────────

class RepairScreen extends StatelessWidget {
  const RepairScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Targeted Error Repair'), backgroundColor: Colors.transparent),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.build, color: Colors.redAccent, size: 64),
            const SizedBox(height: 16),
            const Text('Repair Error Patterns', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.push('/exercise/ex_repair_1'),
              child: const Text('Start Repair Session'),
            ),
          ],
        ),
      ),
    );
  }
}

// ── 13. REVIEW SCREEN ──────────────────────────────────────────────────────

class ReviewScreen extends StatelessWidget {
  const ReviewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Spaced Repetition Review'), backgroundColor: Colors.transparent),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.replay, color: Colors.purple, size: 64),
            const SizedBox(height: 16),
            const Text('Review Memory Targets', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.push('/exercise/ex_review_1'),
              child: const Text('Start Review Session'),
            ),
          ],
        ),
      ),
    );
  }
}

// ── 14. PROGRESS SCREEN ────────────────────────────────────────────────────

class ProgressScreen extends StatelessWidget {
  const ProgressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Learner Progress Analytics'), backgroundColor: Colors.transparent),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Overall Accuracy', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 4),
            const Text('85.5%', style: TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            const Text('Level A1 Completion', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 8),
            LinearProgressIndicator(value: 0.65, backgroundColor: AppTheme.darkSurface, color: AppTheme.primaryColor),
          ],
        ),
      ),
    );
  }
}

// ── 15. PLACEMENT TEST SCREEN ──────────────────────────────────────────────

class PlacementTestScreen extends StatelessWidget {
  const PlacementTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Placement Test'), backgroundColor: Colors.transparent),
      body: Center(
        child: ElevatedButton(
          onPressed: () => context.push('/exercise/ex_place_1'),
          child: const Text('Begin Placement Test'),
        ),
      ),
    );
  }
}

// ── 16. DIAGNOSTIC ASSESSMENT SCREEN ──────────────────────────────────────

class DiagnosticAssessmentScreen extends StatelessWidget {
  const DiagnosticAssessmentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Diagnostic Assessment'), backgroundColor: Colors.transparent),
      body: Center(
        child: ElevatedButton(
          onPressed: () => context.push('/exercise/ex_diag_1'),
          child: const Text('Begin Diagnostic Test'),
        ),
      ),
    );
  }
}

// ── 17. CHECKPOINT TEST SCREEN ─────────────────────────────────────────────

class CheckpointTestScreen extends StatelessWidget {
  const CheckpointTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Checkpoint Test'), backgroundColor: Colors.transparent),
      body: Center(
        child: ElevatedButton(
          onPressed: () => context.push('/exercise/ex_check_1'),
          child: const Text('Begin Checkpoint Test'),
        ),
      ),
    );
  }
}

// ── 18. LEVEL ASSESSMENT SCREEN ────────────────────────────────────────────

class LevelAssessmentScreen extends StatelessWidget {
  const LevelAssessmentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Level Assessment'), backgroundColor: Colors.transparent),
      body: Center(
        child: ElevatedButton(
          onPressed: () => context.push('/exercise/ex_level_1'),
          child: const Text('Begin Level Assessment'),
        ),
      ),
    );
  }
}

// ── 19. LISTENING PRACTICE SCREEN ──────────────────────────────────────────

class ListeningPracticeScreen extends StatelessWidget {
  const ListeningPracticeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Listening Practice'), backgroundColor: Colors.transparent),
      body: Center(
        child: Semantics(
          label: 'Play Listening Audio Practice',
          hint: 'Tap to start audio sentence playback',
          button: true,
          child: AccessibleTouchTarget(
            onTap: () {},
            child: const Icon(Icons.play_circle_fill, color: AppTheme.primaryColor, size: 64),
          ),
        ),
      ),
    );
  }
}

// ── 20. SPEAKING PRACTICE SCREEN ───────────────────────────────────────────

class SpeakingPracticeScreen extends StatelessWidget {
  const SpeakingPracticeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Speaking Practice'), backgroundColor: Colors.transparent),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Semantics(
              label: 'Microphone for Pronunciation Recording',
              hint: 'Hold down to record your speech attempt',
              button: true,
              child: AccessibleTouchTarget(
                onTap: () {},
                child: const Icon(Icons.mic, color: Colors.deepOrange, size: 64),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: () {}, child: const Text('Hold to Record')),
          ],
        ),
      ),
    );
  }
}

// ── 21. WRITING PRACTICE SCREEN ────────────────────────────────────────────

class WritingPracticeScreen extends StatelessWidget {
  const WritingPracticeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Writing Practice'), backgroundColor: Colors.transparent),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Semantics(
              label: 'Writing Input Box',
              hint: 'Type your response here',
              child: const TextField(
                maxLines: 4,
                style: TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Write a short paragraph about your day...',
                  hintStyle: TextStyle(color: Colors.grey),
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: () {}, child: const Text('Submit for Evaluation')),
          ],
        ),
      ),
    );
  }
}

// ── 22. SEARCH SCREEN ──────────────────────────────────────────────────────

class SearchScreen extends ConsumerWidget {
  const SearchScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final results = ref.watch(searchProvider);

    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(
        title: TextField(
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(hintText: 'Search curriculum targets...', hintStyle: TextStyle(color: Colors.grey), border: InputBorder.none),
          onChanged: (val) => ref.read(searchProvider.notifier).query(val),
        ),
        backgroundColor: Colors.transparent,
      ),
      body: ListView.builder(
        itemCount: results.length,
        itemBuilder: (context, index) {
          final res = results[index];
          return ListTile(
            title: Text(res['title'] ?? '', style: const TextStyle(color: Colors.white)),
            subtitle: Text('${res['target_type']} • Level ${res['level']}', style: const TextStyle(color: Colors.grey)),
          );
        },
      ),
    );
  }
}

// ── 23. BOOKMARKS SCREEN ───────────────────────────────────────────────────

class BookmarksScreen extends ConsumerWidget {
  const BookmarksScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final bookmarks = ref.watch(bookmarkProvider);

    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Bookmarks'), backgroundColor: Colors.transparent),
      body: bookmarks.isEmpty
          ? const Center(child: Text('No bookmarks saved yet.', style: TextStyle(color: Colors.grey)))
          : ListView.builder(
              itemCount: bookmarks.length,
              itemBuilder: (context, index) {
                final bm = bookmarks[index];
                return ListTile(
                  title: Text(bm['title'] ?? '', style: const TextStyle(color: Colors.white)),
                  subtitle: Text(bm['item_type'] ?? '', style: const TextStyle(color: Colors.grey)),
                );
              },
            ),
    );
  }
}

// ── 24. HISTORY SCREEN ─────────────────────────────────────────────────────

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('Learning History'), backgroundColor: Colors.transparent),
      body: const Center(child: Text('Learning History Timeline', style: TextStyle(color: Colors.white))),
    );
  }
}

// ── 25. SETTINGS SCREEN ────────────────────────────────────────────────────

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);

    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('User Settings'), backgroundColor: Colors.transparent),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          SwitchListTile(
            title: const Text('Daily Reminders', style: TextStyle(color: Colors.white)),
            value: settings.remindersEnabled,
            onChanged: (val) => ref.read(settingsProvider.notifier).updateSettings('user_default_01', {'reminders_enabled': val}),
          ),
          SwitchListTile(
            title: const Text('Audio Autoplay', style: TextStyle(color: Colors.white)),
            value: settings.audioAutoplay,
            onChanged: (val) => ref.read(settingsProvider.notifier).updateSettings('user_default_01', {'audio_autoplay': val}),
          ),
          SwitchListTile(
            title: const Text('High Contrast UI', style: TextStyle(color: Colors.white)),
            value: settings.accessibilityHighContrast,
            onChanged: (val) => ref.read(settingsProvider.notifier).updateSettings('user_default_01', {'accessibility_high_contrast': val}),
          ),
        ],
      ),
    );
  }
}

// ── 26. REPORT ISSUE DIALOG ────────────────────────────────────────────────

class ReportIssueDialog extends StatelessWidget {
  final String lessonId;
  const ReportIssueDialog({super.key, required this.lessonId});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: AppTheme.darkSurface,
      title: const Text('Report Content Issue', style: TextStyle(color: Colors.white)),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: const [
          TextField(
            style: TextStyle(color: Colors.white),
            decoration: InputDecoration(hintText: 'Describe issue (typo, audio, wrong answer)...', hintStyle: TextStyle(color: Colors.grey)),
          ),
        ],
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        ElevatedButton(
          onPressed: () {
            Navigator.pop(context);
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Report submitted. Thank you!')));
          },
          child: const Text('Submit Report'),
        ),
      ],
    );
  }
}
