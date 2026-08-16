// lib/features/grammar/screens/grammar_detail_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/services/supabase_service.dart';
import '../../../core/constants/app_constants.dart';
import '../../../shared/widgets/loading_shimmer.dart';

class GrammarDetailScreen extends StatefulWidget {
  final String languageId;
  final String levelId;
  final String topicId;

  const GrammarDetailScreen({
    super.key,
    required this.languageId,
    required this.levelId,
    required this.topicId,
  });

  @override
  State<GrammarDetailScreen> createState() => _GrammarDetailScreenState();
}

class _GrammarDetailScreenState extends State<GrammarDetailScreen>
    with SingleTickerProviderStateMixin {
  Map<String, dynamic>? _content;
  Map<String, dynamic>? _contrast;
  bool _isLoading = true;
  String? _error;
  String _nativeLanguage = 'fa';
  late TabController _tabController;

  static const Map<String, Color> _levelColors = {
    'A1': Color(0xFF10B981),
    'A2': Color(0xFF06B6D4),
    'B1': Color(0xFF3B82F6),
    'B2': Color(0xFF8B5CF6),
    'C1': Color(0xFFEC4899),
    'C2': Color(0xFFF59E0B),
  };

  Color get _levelColor => _levelColors[widget.levelId] ?? AppTheme.primaryPurple;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _init();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _init() async {
    final prefs = await SharedPreferences.getInstance();
    _nativeLanguage = prefs.getString(AppConstants.keyNativeLanguage) ?? 'fa';
    await _loadContent();
  }

  Future<void> _loadContent() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final results = await Future.wait([
        SupabaseService.getGrammarContent(
          topicId: widget.topicId,
          nativeLanguage: _nativeLanguage,
        ),
        if (AppConstants.grammarContrastLevels.contains(widget.levelId))
          SupabaseService.getGrammarContrast(
            topicId: widget.topicId,
            targetLanguage: widget.languageId,
            nativeLanguage: _nativeLanguage,
          )
        else
          Future.value(null),
      ]);
      if (mounted) {
        setState(() {
          _content = results[0];
          _contrast = results[1];
          _isLoading = false;
        });
      }
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
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(context),
              Expanded(child: _buildBody()),
            ],
          ),
        ),
      ),
      // Practice button at the bottom
      bottomNavigationBar: _buildPracticeBar(context),
    );
  }

  Widget _buildHeader(BuildContext context) {
    final topicTitle = _content?['topic_title'] as String? ?? 'Grammar';

    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 12, 16, 0),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded,
                color: AppTheme.darkTextSub, size: 20),
            onPressed: () {
              if (context.canPop()) {
                context.pop();
              } else {
                context.go('/grammar/${widget.languageId}/${widget.levelId}');
              }
            },
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: _levelColor.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: _levelColor.withOpacity(0.4)),
                      ),
                      child: Text(
                        widget.levelId,
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: _levelColor,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Grammar',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12,
                        color: AppTheme.darkTextSub,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  topicTitle,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.darkText,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          // Native language chip
          GestureDetector(
            onTap: _showLanguagePicker,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: AppTheme.darkCard,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppTheme.darkCardBorder),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(_nativeLangFlag(), style: const TextStyle(fontSize: 14)),
                  const SizedBox(width: 4),
                  const Icon(Icons.keyboard_arrow_down_rounded,
                      size: 16, color: AppTheme.darkTextSub),
                ],
              ),
            ),
          ),
        ],
      ).animate().fadeIn(duration: 300.ms),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const SizedBox(height: 12),
            LoadingShimmerCard(height: 160),
            LoadingShimmerCard(height: 120),
            LoadingShimmerCard(height: 200),
          ],
        ),
      );
    }

    if (_error != null) return _buildError();
    if (_content == null) return _buildNoContent();

    return _buildExplanationTab();
  }

  Widget _buildExplanationTab() {
    final isRtl = AppConstants.rtlLanguages.contains(_nativeLanguage);
    final explanation = _content?['explanation'] as String? ?? '';
    final comparison = (_content?['comparison'] ?? _content?['native_comparison']) as String? ?? '';
    final examples = ((_content?['examples_json'] ?? _content?['examples']) as List?)?.cast<dynamic>() ?? [];
    final tips = ((_content?['tips_json'] ?? _content?['tips']) as List?)?.cast<dynamic>() ?? [];
    final mistakes = ((_content?['common_mistakes_json'] ?? _content?['common_mistakes']) as List?)?.cast<dynamic>() ?? [];
    final rules = (_content?['rules'] as List?)?.cast<dynamic>() ?? [];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 12),

          // Native Language Explanation
          if (explanation.isNotEmpty) ...[
            _SectionHeader(
              title: _nativeLanguage == 'fa' ? 'توضیحات گرامر (به زبان مادری)' : 'Grammar Explanation',
              icon: Icons.lightbulb_outline_rounded,
              color: _levelColor,
            ),
            const SizedBox(height: 12),
            _ContentCard(text: explanation, levelColor: _levelColor, isRtl: isRtl),
            const SizedBox(height: 20),
          ],

          // Native Language Grammar Comparison & 2 Examples (For A1-A2)
          if (comparison.isNotEmpty || widget.levelId == 'A1' || widget.levelId == 'A2') ...[
            _SectionHeader(
              title: _nativeLanguage == 'fa'
                  ? 'تفاوت گرامر با زبان مادری (مقایسه ۲ مثال)'
                  : 'Grammar Difference with Native Language (2 Examples)',
              icon: Icons.compare_arrows_rounded,
              color: AppTheme.primaryTeal,
            ),
            const SizedBox(height: 12),
            if (comparison.isNotEmpty)
              _ContentCard(
                text: comparison,
                levelColor: AppTheme.primaryTeal,
                isRtl: isRtl,
              ),
            if (examples.isNotEmpty) ...[
              const SizedBox(height: 12),
              ...examples.take(2).map((ex) => _ExampleCard(
                example: ex is Map ? ex : {'target': ex.toString()},
                levelColor: AppTheme.primaryTeal,
                isRtl: isRtl,
                showNative: true,
              )),
            ],
            const SizedBox(height: 20),
          ],

          // Key Rules / Tips
          if (tips.isNotEmpty) ...[
            _SectionHeader(title: 'Key Tips', icon: Icons.tips_and_updates_rounded, color: AppTheme.accentAmber),
            const SizedBox(height: 12),
            ...tips.map((t) => _TipCard(
              text: t is Map ? '${t['tip'] ?? ''}\nExample: ${t['example'] ?? ''}' : t.toString(),
              isRtl: isRtl,
            )),
            const SizedBox(height: 20),
          ] else if (rules.isNotEmpty) ...[
            _SectionHeader(title: 'Key Rules', icon: Icons.rule_rounded, color: _levelColor),
            const SizedBox(height: 12),
            ...rules.asMap().entries.map((e) => _RuleItem(
              index: e.key + 1,
              text: e.value.toString(),
              color: _levelColor,
              isRtl: isRtl,
            )),
            const SizedBox(height: 20),
          ],

          // Examples
          if (examples.isNotEmpty) ...[
            _SectionHeader(title: 'Examples', icon: Icons.format_quote_rounded,
                color: _levelColor),
            const SizedBox(height: 12),
            ...examples.map((ex) => _ExampleCard(
              example: ex is Map ? ex : {'target': ex.toString()},
              levelColor: _levelColor,
              isRtl: isRtl,
            )),
          ],

          // Common Mistakes
          if (mistakes.isNotEmpty) ...[
            const SizedBox(height: 20),
            _SectionHeader(title: 'Common Mistakes', icon: Icons.warning_amber_rounded, color: AppTheme.colorError),
            const SizedBox(height: 12),
            ...mistakes.map((m) => Directionality(
              textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
              child: Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.colorError.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppTheme.colorError.withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.close_rounded, size: 16, color: AppTheme.colorError),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            m is Map ? (m['wrong'] ?? '') : m.toString(),
                            style: const TextStyle(fontFamily: 'Outfit', color: AppTheme.colorError, decoration: TextDecoration.lineThrough),
                          ),
                        ),
                      ],
                    ),
                    if (m is Map && (m['right'] != null)) ...[
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Icon(Icons.check_rounded, size: 16, color: AppTheme.colorSuccess),
                          const SizedBox(width: 6),
                          Expanded(
                            child: Text(
                              m['right'].toString(),
                              style: const TextStyle(fontFamily: 'Outfit', color: AppTheme.colorSuccess, fontWeight: FontWeight.w600),
                            ),
                          ),
                        ],
                      ),
                    ],
                    if (m is Map && (m['reason'] != null)) ...[
                      const SizedBox(height: 4),
                      Text(
                        m['reason'].toString(),
                        textAlign: isRtl ? TextAlign.right : TextAlign.left,
                        style: const TextStyle(fontFamily: 'Outfit', fontSize: 12, color: AppTheme.darkTextSub),
                      ),
                    ],
                  ],
                ),
              ),
            )),
          ],

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildExamplesSection() {
    final examples = (_content?['examples'] as List?)?.cast<dynamic>() ?? [];
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 12),
          if (examples.isEmpty)
            _buildNoContent()
          else
            ...examples.map((ex) => _ExampleCard(
              example: ex is Map ? ex : {'target': ex.toString()},
              levelColor: _levelColor,
            )),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildContrastTab() {
    if (_contrast == null) {
      return _buildNoContent(
        message: 'Comparison with your language is being prepared.',
      );
    }

    final differences = (_contrast?['differences'] as List?)?.cast<dynamic>() ?? [];
    final tips = (_contrast?['tips'] as List?)?.cast<dynamic>() ?? [];
    final contrastExamples = (_contrast?['examples'] as List?)?.cast<dynamic>() ?? [];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 12),

          // Info banner
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.primaryTeal.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.primaryTeal.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                const Icon(Icons.compare_arrows_rounded,
                    color: AppTheme.primaryTeal, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'How this grammar differs from your native language',
                    style: const TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 13,
                      color: AppTheme.primaryTeal,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          if (differences.isNotEmpty) ...[
            _SectionHeader(title: 'Key Differences', icon: Icons.difference_rounded,
                color: _levelColor),
            const SizedBox(height: 12),
            ...differences.asMap().entries.map((e) => _RuleItem(
              index: e.key + 1,
              text: e.value.toString(),
              color: AppTheme.accentRose,
            )),
            const SizedBox(height: 20),
          ],

          if (contrastExamples.isNotEmpty) ...[
            _SectionHeader(title: 'Side by Side', icon: Icons.view_column_rounded,
                color: _levelColor),
            const SizedBox(height: 12),
            ...contrastExamples.map((ex) => _ExampleCard(
              example: ex is Map ? ex : {'target': ex.toString()},
              levelColor: _levelColor,
              showNative: true,
            )),
            const SizedBox(height: 20),
          ],

          if (tips.isNotEmpty) ...[
            _SectionHeader(title: 'Tips', icon: Icons.tips_and_updates_rounded,
                color: AppTheme.accentAmber),
            const SizedBox(height: 12),
            ...tips.map((tip) => _TipCard(text: tip.toString())),
          ],

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildNoContent({String? message}) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: _levelColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.hourglass_empty_rounded, size: 32, color: _levelColor),
            ),
            const SizedBox(height: 16),
            const Text('Content Not Ready Yet',
                style: TextStyle(fontFamily: 'Outfit', fontSize: 18,
                    fontWeight: FontWeight.w600, color: AppTheme.darkText)),
            const SizedBox(height: 8),
            Text(
              message ?? 'This topic is being prepared by AI.\nCheck back soon!',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: AppTheme.darkTextSub, height: 1.6),
            ),
          ],
        ).animate().fadeIn(duration: 400.ms),
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded, size: 48, color: AppTheme.colorError),
            const SizedBox(height: 16),
            const Text('Failed to load content',
                style: TextStyle(fontFamily: 'Outfit', fontSize: 18,
                    fontWeight: FontWeight.w600, color: AppTheme.darkText)),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadContent,
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

  Widget _buildPracticeBar(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
      decoration: BoxDecoration(
        color: AppTheme.darkSurface,
        border: const Border(top: BorderSide(color: AppTheme.darkCardBorder)),
      ),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton.icon(
              onPressed: () => context.push(
                '/exercises/${widget.languageId}/${widget.levelId}?topicId=${widget.topicId}&mode=practice',
              ),
              icon: const Icon(Icons.fitness_center_rounded, size: 18),
              label: const Text('Practice'),
              style: OutlinedButton.styleFrom(
                foregroundColor: _levelColor,
                side: BorderSide(color: _levelColor),
                minimumSize: const Size(0, 50),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: ElevatedButton.icon(
              onPressed: () => context.push(
                '/exercises/mc/${widget.languageId}/${widget.levelId}?topicId=${widget.topicId}&mode=quiz',
              ),
              icon: const Icon(Icons.quiz_rounded, size: 18),
              label: const Text('Quick Quiz'),
              style: ElevatedButton.styleFrom(
                backgroundColor: _levelColor,
                foregroundColor: Colors.white,
                minimumSize: const Size(0, 50),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                elevation: 0,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _nativeLangFlag() {
    const flags = {
      'fa': '🇮🇷', 'da': '🇩🇰', 'en': '🇬🇧', 'ar': '🇸🇦',
      'fr': '🇫🇷', 'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸',
    };
    return flags[_nativeLanguage] ?? '🌐';
  }

  void _showLanguagePicker() {
    final langs = [
      {'code': 'fa', 'name': 'فارسی', 'flag': '🇮🇷'},
      {'code': 'da', 'name': 'دانمارکی (Dansk)', 'flag': '🇩🇰'},
      {'code': 'en', 'name': 'English', 'flag': '🇬🇧'},
      {'code': 'ar', 'name': 'العربية', 'flag': '🇸🇦'},
    ];
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.darkCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Explanation Language',
                style: TextStyle(fontFamily: 'Outfit', fontSize: 16,
                    fontWeight: FontWeight.w600, color: AppTheme.darkText)),
            const SizedBox(height: 16),
            ...langs.map((l) => ListTile(
              leading: Text(l['flag']!, style: const TextStyle(fontSize: 22)),
              title: Text(l['name']!,
                  style: const TextStyle(fontFamily: 'Outfit', color: AppTheme.darkText)),
              trailing: _nativeLanguage == l['code']
                  ? Icon(Icons.check_circle_rounded, color: _levelColor)
                  : null,
              onTap: () async {
                final prefs = await SharedPreferences.getInstance();
                await prefs.setString(AppConstants.keyNativeLanguage, l['code']!);
                if (mounted) {
                  setState(() => _nativeLanguage = l['code']!);
                  Navigator.pop(ctx);
                  _loadContent();
                }
              },
            )),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}

// ── Reusable Widgets ───────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color color;

  const _SectionHeader({required this.title, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: color),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            title,
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ),
      ],
    );
  }
}

class _ContentCard extends StatelessWidget {
  final String text;
  final Color levelColor;
  final bool isRtl;

  const _ContentCard({
    required this.text,
    required this.levelColor,
    this.isRtl = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: levelColor.withOpacity(0.06),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: levelColor.withOpacity(0.2)),
      ),
      child: Directionality(
        textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
        child: Text(
          text,
          textAlign: isRtl ? TextAlign.right : TextAlign.left,
          style: const TextStyle(
            fontFamily: 'Outfit',
            fontSize: 14,
            color: AppTheme.darkText,
            height: 1.8,
          ),
        ),
      ),
    );
  }
}

class _RuleItem extends StatelessWidget {
  final int index;
  final String text;
  final Color color;
  final bool isRtl;

  const _RuleItem({
    required this.index,
    required this.text,
    required this.color,
    this.isRtl = true,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Directionality(
        textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 24,
              height: 24,
              margin: const EdgeInsets.only(top: 1),
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  '$index',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: color,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                text,
                textAlign: isRtl ? TextAlign.right : TextAlign.left,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 14,
                  color: AppTheme.darkText,
                  height: 1.5,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ExampleCard extends StatelessWidget {
  final Map<dynamic, dynamic> example;
  final Color levelColor;
  final bool showNative;
  final bool isRtl;

  const _ExampleCard({
    required this.example,
    required this.levelColor,
    this.showNative = false,
    this.isRtl = true,
  });

  @override
  Widget build(BuildContext context) {
    final target = example['target']?.toString() ?? '';
    final native = example['native']?.toString() ?? '';
    final note = (example['note'] ?? example['breakdown'])?.toString() ?? '';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.darkCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.darkCardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Target sentence (English LTR)
          Directionality(
            textDirection: TextDirection.ltr,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 4,
                  height: 20,
                  margin: const EdgeInsets.only(top: 2, right: 10),
                  decoration: BoxDecoration(
                    color: levelColor,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                Expanded(
                  child: Text(
                    target,
                    style: const TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                      color: AppTheme.darkText,
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Native translation (Persian RTL)
          if (native.isNotEmpty) ...[
            const SizedBox(height: 6),
            Directionality(
              textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
              child: Padding(
                padding: const EdgeInsets.only(left: 14, right: 14),
                child: Text(
                  native,
                  textAlign: isRtl ? TextAlign.right : TextAlign.left,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 13,
                    color: AppTheme.darkTextSub,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            ),
          ],
          // Note / Breakdown (Persian RTL)
          if (note.isNotEmpty) ...[
            const SizedBox(height: 8),
            Directionality(
              textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: AppTheme.accentAmber.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline_rounded,
                        size: 14, color: AppTheme.accentAmber),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        note,
                        textAlign: isRtl ? TextAlign.right : TextAlign.left,
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 12,
                          color: AppTheme.accentAmber,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _TipCard extends StatelessWidget {
  final String text;
  final bool isRtl;

  const _TipCard({required this.text, this.isRtl = true});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.accentAmber.withOpacity(0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.accentAmber.withOpacity(0.25)),
      ),
      child: Directionality(
        textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(Icons.tips_and_updates_rounded,
                size: 18, color: AppTheme.accentAmber),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                text,
                textAlign: isRtl ? TextAlign.right : TextAlign.left,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 13,
                  color: AppTheme.darkText,
                  height: 1.5,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
