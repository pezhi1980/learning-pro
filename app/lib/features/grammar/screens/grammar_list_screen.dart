// lib/features/grammar/screens/grammar_list_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/services/supabase_service.dart';
import '../../../core/utils/router.dart';
import '../../../shared/widgets/loading_shimmer.dart';

class GrammarListScreen extends StatefulWidget {
  final String languageId;
  final String levelId;

  const GrammarListScreen({
    super.key,
    required this.languageId,
    required this.levelId,
  });

  @override
  State<GrammarListScreen> createState() => _GrammarListScreenState();
}

class _GrammarListScreenState extends State<GrammarListScreen> {
  List<Map<String, dynamic>> _topics = [];
  bool _isLoading = true;
  String? _error;

  // Level colors map
  static const Map<String, Color> _levelColors = {
    'A1': Color(0xFF10B981),
    'A2': Color(0xFF06B6D4),
    'B1': Color(0xFF3B82F6),
    'B2': Color(0xFF8B5CF6),
    'C1': Color(0xFFEC4899),
    'C2': Color(0xFFF59E0B),
  };

  Color get _levelColor => _levelColors[widget.levelId] ?? AppTheme.primaryPurple;

  String get _languageFlag {
    const flags = {'en': '🇬🇧', 'fr': '🇫🇷', 'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸'};
    return flags[widget.languageId] ?? '🌐';
  }

  @override
  void initState() {
    super.initState();
    _loadTopics();
  }

  Future<void> _loadTopics() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final data = await SupabaseService.getGrammarTopics(
        languageId: widget.languageId,
        levelId: widget.levelId,
      );
      if (mounted) setState(() { _topics = data; _isLoading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.darkBgGradient),
        child: Stack(
          children: [
            // Level-colored background blob
            Positioned(
              top: -80,
              right: -80,
              child: Container(
                width: 260,
                height: 260,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(colors: [
                    _levelColor.withOpacity(0.15),
                    Colors.transparent,
                  ]),
                ),
              ),
            ),
            SafeArea(
              child: Column(
                children: [
                  _buildHeader(context),
                  const SizedBox(height: 8),
                  // Tab bar: Grammar | Vocabulary | Exercises
                  _buildSectionTabs(context),
                  const SizedBox(height: 16),
                  Expanded(child: _buildBody()),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 16, 16, 0),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded,
                color: AppTheme.darkTextSub, size: 20),
            onPressed: () {
              if (context.canPop()) {
                context.pop();
              } else {
                context.go('/levels/${widget.languageId}');
              }
            },
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(_languageFlag, style: const TextStyle(fontSize: 18)),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: _levelColor.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: _levelColor.withOpacity(0.4)),
                      ),
                      child: Text(
                        widget.levelId,
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: _levelColor,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                const Text(
                  'Grammar',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.darkText,
                  ),
                ),
              ],
            ),
          ),
          // Exercise shortcut button
          IconButton(
            icon: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.darkCard,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.darkCardBorder),
              ),
              child: const Icon(Icons.fitness_center_rounded,
                  size: 18, color: AppTheme.darkTextSub),
            ),
            onPressed: () => context.go(
              '/exercises/${widget.languageId}/${widget.levelId}',
            ),
          ),
        ],
      ).animate().fadeIn(duration: 300.ms),
    );
  }

  Widget _buildSectionTabs(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Container(
        padding: const EdgeInsets.all(4),
        decoration: BoxDecoration(
          color: AppTheme.darkCard,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.darkCardBorder),
        ),
        child: Row(
          children: [
            _TabItem(
              label: 'Grammar',
              icon: Icons.menu_book_rounded,
              isActive: true,
              color: _levelColor,
              onTap: () {},
            ),
            _TabItem(
              label: 'Vocabulary',
              icon: Icons.abc_rounded,
              isActive: false,
              color: _levelColor,
              onTap: () => context.go(
                '/vocabulary/${widget.languageId}/${widget.levelId}',
              ),
            ),
            _TabItem(
              label: 'Flashcards',
              icon: Icons.style_rounded,
              isActive: false,
              color: _levelColor,
              onTap: () => context.go(
                '/flashcards/${widget.languageId}/${widget.levelId}',
              ),
            ),
          ],
        ),
      ).animate().fadeIn(delay: 150.ms),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: LoadingShimmerList(count: 6, cardHeight: 88),
      );
    }

    if (_error != null) {
      return _buildError();
    }

    if (_topics.isEmpty) {
      return _buildEmpty();
    }

    return RefreshIndicator(
      onRefresh: _loadTopics,
      color: _levelColor,
      backgroundColor: AppTheme.darkCard,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        itemCount: _topics.length,
        itemBuilder: (ctx, i) {
          final topic = _topics[i];
          return _GrammarTopicCard(
            topic: topic,
            levelColor: _levelColor,
            animDelay: (i * 60).ms,
            onTap: () => context.go(
              '/grammar/${widget.languageId}/${widget.levelId}/${topic['id']}',
            ),
          );
        },
      ),
    );
  }

  Widget _buildEmpty() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: _levelColor.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.construction_rounded, size: 36, color: _levelColor),
          ),
          const SizedBox(height: 20),
          const Text(
            'Content Coming Soon',
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 20,
              fontWeight: FontWeight.w600,
              color: AppTheme.darkText,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Grammar topics for ${widget.levelId} are being prepared.\nCheck back soon!',
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontFamily: 'Outfit',
              fontSize: 14,
              color: AppTheme.darkTextSub,
              height: 1.6,
            ),
          ),
        ],
      ).animate().fadeIn(duration: 400.ms).scale(begin: const Offset(0.9, 0.9)),
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.wifi_off_rounded, size: 48, color: AppTheme.colorError),
            const SizedBox(height: 16),
            const Text('Could not load topics',
                style: TextStyle(fontFamily: 'Outfit', fontSize: 18,
                    fontWeight: FontWeight.w600, color: AppTheme.darkText)),
            const SizedBox(height: 8),
            Text(_error ?? '',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 13, color: AppTheme.darkTextSub)),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadTopics,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: _levelColor,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Tab Item ───────────────────────────────────────────────

class _TabItem extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isActive;
  final Color color;
  final VoidCallback onTap;

  const _TabItem({
    required this.label,
    required this.icon,
    required this.isActive,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: isActive ? color.withOpacity(0.15) : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Column(
            children: [
              Icon(icon, size: 18,
                  color: isActive ? color : AppTheme.darkTextSub),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 11,
                  fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
                  color: isActive ? color : AppTheme.darkTextSub,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

const Map<String, String> _topicTitles = {
  'verb_to_be_present': 'Verb to Be (Present Tense)',
  'personal_pronouns': 'Personal Pronouns',
  'indefinite_articles': 'Indefinite Articles (a / an)',
  'definite_article': 'Definite Article (the)',
  'plural_nouns': 'Plural Nouns (Regular & Irregular)',
  'possessive_adjectives': 'Possessive Adjectives',
  'demonstratives': 'Demonstratives (this, that, these, those)',
  'present_simple_affirmative': 'Present Simple (Affirmative)',
  'present_simple_negative': 'Present Simple (Negative)',
  'present_simple_questions': 'Present Simple (Questions)',
  'have_got': 'Have got / Has got',
  'can_ability': 'Modal Verb: Can (Ability)',
  'imperative': 'Imperative Sentences',
  'there_is_there_are': 'There is / There are',
  'basic_prepositions_place': 'Prepositions of Place (in, on, at)',
  'adjectives_basic': 'Basic Adjectives & Position',
  'numbers_and_quantity': 'Numbers & Quantity (some / any)',
  'wh_questions': 'Question Words (Who, What, Where, When, Why)',
  'object_pronouns': 'Object Pronouns (me, him, her, us, them)',
  'like_and_want': 'Expressing Likes & Desires (like / want)',
};

String _formatTopicTitle(String topicCode) {
  if (_topicTitles.containsKey(topicCode)) return _topicTitles[topicCode]!;
  return topicCode
      .split('_')
      .map((w) => w.isNotEmpty ? w[0].toUpperCase() + w.substring(1) : '')
      .join(' ');
}

// ── Grammar Topic Card ─────────────────────────────────────

class _GrammarTopicCard extends StatelessWidget {
  final Map<String, dynamic> topic;
  final Color levelColor;
  final Duration animDelay;
  final VoidCallback onTap;

  const _GrammarTopicCard({
    required this.topic,
    required this.levelColor,
    required this.animDelay,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final topicCode = topic['topic_code'] as String? ?? '';
    final rawTitle = topic['title'] as String?;
    final title = (rawTitle != null && rawTitle.isNotEmpty && rawTitle != 'Topic')
        ? rawTitle
        : _formatTopicTitle(topicCode);
    final description = topic['description'] as String? ?? '';
    final orderIndex = topic['order_index'] as int? ?? 0;
    final exerciseCount = topic['exercise_count'] as int? ?? 0;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.darkCard,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppTheme.darkCardBorder),
          ),
          child: Row(
            children: [
              // Number badge
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: levelColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    '$orderIndex',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: levelColor,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 14),
              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.darkText,
                      ),
                    ),
                    if (description.isNotEmpty) ...[
                      const SizedBox(height: 3),
                      Text(
                        description,
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 12,
                          color: AppTheme.darkTextSub,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    if (exerciseCount > 0) ...[
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          Icon(Icons.quiz_rounded, size: 12, color: levelColor),
                          const SizedBox(width: 4),
                          Text(
                            '$exerciseCount exercises',
                            style: TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 11,
                              color: levelColor,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              Icon(Icons.chevron_right_rounded,
                  color: AppTheme.darkTextSub.withOpacity(0.5)),
            ],
          ),
        ),
      ),
    )
        .animate()
        .fadeIn(delay: animDelay, duration: 350.ms)
        .slideX(begin: 0.1, end: 0, delay: animDelay, duration: 350.ms);
  }
}
