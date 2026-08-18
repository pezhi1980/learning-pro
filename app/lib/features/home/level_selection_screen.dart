// lib/features/home/level_selection_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/localization_helper.dart';

class LevelSelectionScreen extends StatefulWidget {
  final String languageId;
  const LevelSelectionScreen({super.key, required this.languageId});

  @override
  State<LevelSelectionScreen> createState() => _LevelSelectionScreenState();
}

class _LevelSelectionScreenState extends State<LevelSelectionScreen> {
  List<_LevelItem> get _levels => [
    _LevelItem(
      id: 'A1',
      label: LocalizationHelper.tr('level_1_label', lang: LocalizationHelper.currentLang),
      title: LocalizationHelper.tr('level_1_title', lang: LocalizationHelper.currentLang),
      description: LocalizationHelper.tr('level_1_desc', lang: LocalizationHelper.currentLang),
      color: const Color(0xFF10B981),    // emerald
      topics: 20,
      vocab: 500,
    ),
    _LevelItem(
      id: 'A2',
      label: LocalizationHelper.tr('level_2_label', lang: LocalizationHelper.currentLang),
      title: LocalizationHelper.tr('level_2_title', lang: LocalizationHelper.currentLang),
      description: LocalizationHelper.tr('level_2_desc', lang: LocalizationHelper.currentLang),
      color: const Color(0xFF06B6D4),    // cyan
      topics: 28,
      vocab: 1000,
    ),
    _LevelItem(
      id: 'B1',
      label: LocalizationHelper.tr('level_3_label', lang: LocalizationHelper.currentLang),
      title: LocalizationHelper.tr('level_3_title', lang: LocalizationHelper.currentLang),
      description: LocalizationHelper.tr('level_3_desc', lang: LocalizationHelper.currentLang),
      color: const Color(0xFF3B82F6),    // blue
      topics: 35,
      vocab: 2000,
    ),
    _LevelItem(
      id: 'B2',
      label: LocalizationHelper.tr('level_4_label', lang: LocalizationHelper.currentLang),
      title: LocalizationHelper.tr('level_4_title', lang: LocalizationHelper.currentLang),
      description: LocalizationHelper.tr('level_4_desc', lang: LocalizationHelper.currentLang),
      color: const Color(0xFF8B5CF6),    // violet
      topics: 40,
      vocab: 3500,
    ),
    _LevelItem(
      id: 'C1',
      label: LocalizationHelper.tr('level_5_label', lang: LocalizationHelper.currentLang),
      title: LocalizationHelper.tr('level_5_title', lang: LocalizationHelper.currentLang),
      description: LocalizationHelper.tr('level_5_desc', lang: LocalizationHelper.currentLang),
      color: const Color(0xFFEC4899),    // pink
      topics: 45,
      vocab: 5000,
    ),
    _LevelItem(
      id: 'C2',
      label: LocalizationHelper.tr('level_6_label', lang: LocalizationHelper.currentLang),
      title: LocalizationHelper.tr('level_6_title', lang: LocalizationHelper.currentLang),
      description: LocalizationHelper.tr('level_6_desc', lang: LocalizationHelper.currentLang),
      color: const Color(0xFFF59E0B),    // amber
      topics: 30,
      vocab: 8000,
    ),
  ];

  String get _languageName {
    const names = {
      'en': 'English',
      'fr': 'French',
      'de': 'German',
      'it': 'Italian',
      'es': 'Spanish',
    };
    return names[widget.languageId] ?? widget.languageId;
  }

  String get _languageFlag {
    const flags = {
      'en': '🇬🇧',
      'fr': '🇫🇷',
      'de': '🇩🇪',
      'it': '🇮🇹',
      'es': '🇪🇸',
    };
    return flags[widget.languageId] ?? '🌐';
  }

  void _onLevelSelected(String levelId) {
    // Navigate to the level dashboard (grammar list for now)
    context.push('/grammar/${widget.languageId}/$levelId');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.darkBgGradient),
        child: Stack(
          children: [
            // Background blobs
            Positioned(
              top: -60,
              left: -60,
              child: Container(
                width: 240,
                height: 240,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(colors: [
                    AppTheme.primaryTeal.withOpacity(0.15),
                    Colors.transparent,
                  ]),
                ),
              ),
            ),
            Positioned(
              bottom: 100,
              right: -80,
              child: Container(
                width: 260,
                height: 260,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(colors: [
                    AppTheme.primaryPurple.withOpacity(0.12),
                    Colors.transparent,
                  ]),
                ),
              ),
            ),

            SafeArea(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(context),
                  const SizedBox(height: 8),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    child: Text(
                      'Select your current level or the one you want to reach.',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppTheme.darkTextSub,
                          ),
                    ).animate().fadeIn(delay: 200.ms),
                  ),
                  const SizedBox(height: 24),
                  Expanded(
                    child: ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      itemCount: _levels.length,
                      itemBuilder: (context, i) => _LevelCard(
                        level: _levels[i],
                        animDelay: (i * 70).ms,
                        onTap: () => _onLevelSelected(_levels[i].id),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
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
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.arrow_back_ios_new_rounded,
                    color: AppTheme.darkTextSub, size: 20),
                onPressed: () {
                  if (context.canPop()) {
                    context.pop();
                  } else {
                    context.go('/languages');
                  }
                },
                padding: EdgeInsets.zero,
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: AppTheme.darkCard,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: AppTheme.darkCardBorder),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(_languageFlag, style: const TextStyle(fontSize: 16)),
                    const SizedBox(width: 6),
                    Text(
                      _languageName,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: AppTheme.darkText,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ).animate().fadeIn(duration: 300.ms),

          const SizedBox(height: 20),

          Text(
            'Choose Your Level',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  color: AppTheme.darkText,
                  fontWeight: FontWeight.w700,
                ),
          ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.3, end: 0),
        ],
      ),
    );
  }
}

// ── Level Card ──────────────────────────────────────────────

class _LevelCard extends StatelessWidget {
  final _LevelItem level;
  final Duration animDelay;
  final VoidCallback onTap;

  const _LevelCard({
    required this.level,
    required this.animDelay,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: AppTheme.darkCard,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: AppTheme.darkCardBorder),
          ),
          child: Row(
            children: [
              // Level badge
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(14),
                  color: level.color.withOpacity(0.15),
                  border: Border.all(color: level.color.withOpacity(0.4), width: 1.5),
                ),
                child: Center(
                  child: Text(
                    level.label,
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: level.color,
                    ),
                  ),
                ),
              ),

              const SizedBox(width: 16),

              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      level.title,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.darkText,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      level.description,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12,
                        color: AppTheme.darkTextSub,
                        height: 1.4,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    // Stats row
                    Row(
                      children: [
                        _StatChip(
                          icon: Icons.menu_book_rounded,
                          label: '${level.topics} topics',
                          color: level.color,
                        ),
                        const SizedBox(width: 8),
                        _StatChip(
                          icon: Icons.abc_rounded,
                          label: '${level.vocab}+ words',
                          color: level.color,
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(width: 8),
              Icon(
                Icons.chevron_right_rounded,
                color: AppTheme.darkTextSub.withOpacity(0.6),
              ),
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

class _StatChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _StatChip({required this.icon, required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 11,
              fontWeight: FontWeight.w500,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

// ── Data model ─────────────────────────────────────────────

class _LevelItem {
  final String id;
  final String label;
  final String title;
  final String description;
  final Color color;
  final int topics;
  final int vocab;

  const _LevelItem({
    required this.id,
    required this.label,
    required this.title,
    required this.description,
    required this.color,
    required this.topics,
    required this.vocab,
  });
}
