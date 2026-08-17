// lib/features/home/category_selection_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/localization_helper.dart';

class CategorySelectionScreen extends StatefulWidget {
  final String languageId;

  const CategorySelectionScreen({
    super.key,
    required this.languageId,
  });

  @override
  State<CategorySelectionScreen> createState() => _CategorySelectionScreenState();
}

class _CategorySelectionScreenState extends State<CategorySelectionScreen> {
  String _explanationLang = 'en';

  @override
  void initState() {
    super.initState();
    _loadLanguagePreference();
  }

  Future<void> _loadLanguagePreference() async {
    final lang = await LocalizationHelper.getSelectedExplanationLanguage();
    if (mounted) {
      setState(() => _explanationLang = lang);
    }
  }

  void _showExplanationLanguageDialog() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.darkCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  LocalizationHelper.tr('explanation_language', lang: _explanationLang),
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.darkText,
                  ),
                ),
                const SizedBox(height: 16),
                ...LocalizationHelper.nativeLanguageNames.entries.map((entry) {
                  final isSelected = entry.key == _explanationLang;
                  final flag = LocalizationHelper.nativeLanguageFlags[entry.key] ?? '🌐';

                  return ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    leading: Text(flag, style: const TextStyle(fontSize: 24)),
                    title: Text(
                      entry.value,
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 15,
                        fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                        color: isSelected ? AppTheme.primaryTeal : AppTheme.darkText,
                      ),
                    ),
                    trailing: isSelected
                        ? const Icon(Icons.check_circle_rounded, color: AppTheme.primaryTeal)
                        : null,
                    onTap: () async {
                      await LocalizationHelper.setSelectedExplanationLanguage(entry.key);
                      if (mounted) {
                        setState(() => _explanationLang = entry.key);
                      }
                      Navigator.pop(context);
                    },
                  );
                }),
              ],
            ),
          ),
        );
      },
    );
  }

  String get _languageName {
    const names = {
      'en': 'English',
      'fr': 'French',
      'de': 'German',
      'it': 'Italian',
      'es': 'Spanish',
    };
    return names[widget.languageId] ?? widget.languageId.toUpperCase();
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

  @override
  Widget build(BuildContext context) {
    final nativeFlag = LocalizationHelper.nativeLanguageFlags[_explanationLang] ?? '🌐';
    final nativeName = LocalizationHelper.nativeLanguageNames[_explanationLang] ?? _explanationLang;

    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.darkBgGradient),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top navigation bar
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios_new_rounded,
                          color: AppTheme.darkTextSub, size: 20),
                      onPressed: () {
                        if (context.canPop()) {
                          context.pop();
                        } else {
                          context.go('/language-select');
                        }
                      },
                    ),
                    const Spacer(),
                    // Explanation language selector chip
                    GestureDetector(
                      onTap: _showExplanationLanguageDialog,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppTheme.darkCard,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppTheme.primaryTeal.withOpacity(0.4)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(nativeFlag, style: const TextStyle(fontSize: 16)),
                            const SizedBox(width: 6),
                            Text(
                              nativeName.split(' ').first,
                              style: const TextStyle(
                                fontFamily: 'Outfit',
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: AppTheme.primaryTeal,
                              ),
                            ),
                            const SizedBox(width: 4),
                            const Icon(Icons.keyboard_arrow_down_rounded,
                                size: 16, color: AppTheme.primaryTeal),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Target learning language
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
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
                              fontWeight: FontWeight.w600,
                              color: AppTheme.darkText,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ).animate().fadeIn(duration: 300.ms),

                const SizedBox(height: 28),

                // Header title
                Text(
                  LocalizationHelper.tr('your_choice', lang: _explanationLang),
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontFamily: 'Outfit',
                        color: AppTheme.darkText,
                        fontWeight: FontWeight.w700,
                      ),
                ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2, end: 0),

                const SizedBox(height: 8),

                Text(
                  LocalizationHelper.tr('choose_section', lang: _explanationLang),
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontFamily: 'Outfit',
                        color: AppTheme.darkTextSub,
                      ),
                ).animate().fadeIn(delay: 200.ms),

                const SizedBox(height: 32),

                // Category options
                Expanded(
                  child: ListView(
                    physics: const BouncingScrollPhysics(),
                    children: [
                      // Grammar Option
                      _CategoryCard(
                        title: LocalizationHelper.tr('grammar_title', lang: _explanationLang),
                        subtitle: LocalizationHelper.tr('grammar_desc', lang: _explanationLang),
                        icon: Icons.menu_book_rounded,
                        accentGradient: const LinearGradient(
                          colors: [Color(0xFF8B5CF6), Color(0xFF6366F1)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        badgeText: LocalizationHelper.tr('grammar_badge', lang: _explanationLang),
                        enterText: LocalizationHelper.tr('enter_section', lang: _explanationLang),
                        onTap: () {
                          context.push('/levels/${widget.languageId}');
                        },
                      ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.2, end: 0),

                      const SizedBox(height: 20),

                      // Vocabulary Option
                      _CategoryCard(
                        title: LocalizationHelper.tr('vocab_title', lang: _explanationLang),
                        subtitle: LocalizationHelper.tr('vocab_desc', lang: _explanationLang),
                        icon: Icons.style_rounded,
                        accentGradient: const LinearGradient(
                          colors: [Color(0xFF06B6D4), Color(0xFF10B981)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        badgeText: LocalizationHelper.tr('vocab_badge', lang: _explanationLang),
                        enterText: LocalizationHelper.tr('enter_section', lang: _explanationLang),
                        onTap: () {
                          context.push('/vocabulary/${widget.languageId}/A1');
                        },
                      ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.2, end: 0),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _CategoryCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final LinearGradient accentGradient;
  final String badgeText;
  final String enterText;
  final VoidCallback onTap;

  const _CategoryCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.accentGradient,
    required this.badgeText,
    required this.enterText,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.darkCard,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppTheme.darkCardBorder),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 16,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(24),
        child: InkWell(
          borderRadius: BorderRadius.circular(24),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(
                        gradient: accentGradient,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: accentGradient.colors.first.withOpacity(0.4),
                            blurRadius: 12,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Icon(icon, color: Colors.white, size: 28),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: accentGradient.colors.first.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: accentGradient.colors.first.withOpacity(0.3)),
                      ),
                      child: Text(
                        badgeText,
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: accentGradient.colors.first,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                Text(
                  title,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.darkText,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 14,
                    color: AppTheme.darkTextSub,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Text(
                      enterText,
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: accentGradient.colors.first,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Icon(
                      Icons.arrow_forward_rounded,
                      size: 18,
                      color: accentGradient.colors.first,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
