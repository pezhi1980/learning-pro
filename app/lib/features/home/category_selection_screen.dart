// lib/features/home/category_selection_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/app_theme.dart';

class CategorySelectionScreen extends StatelessWidget {
  final String languageId;

  const CategorySelectionScreen({
    super.key,
    required this.languageId,
  });

  String get _languageName {
    const names = {
      'en': 'English',
      'fr': 'French',
      'de': 'German',
      'it': 'Italian',
      'es': 'Spanish',
    };
    return names[languageId] ?? languageId.toUpperCase();
  }

  String get _languageFlag {
    const flags = {
      'en': '🇬🇧',
      'fr': '🇫🇷',
      'de': '🇩🇪',
      'it': '🇮🇹',
      'es': '🇪🇸',
    };
    return flags[languageId] ?? '🌐';
  }

  @override
  Widget build(BuildContext context) {
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
                    Container(
                      padding:
                          const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppTheme.darkCard,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppTheme.darkCardBorder),
                      ),
                      child: Row(
                        children: [
                          Text(_languageFlag, style: const TextStyle(fontSize: 18)),
                          const SizedBox(width: 6),
                          Text(
                            _languageName,
                            style: const TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: AppTheme.darkText,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ).animate().fadeIn(duration: 300.ms),

                const SizedBox(height: 32),

                // Header title
                Text(
                  'حق انتخاب شما ✨',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontFamily: 'Outfit',
                        color: AppTheme.darkText,
                        fontWeight: FontWeight.w700,
                      ),
                ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2, end: 0),

                const SizedBox(height: 8),

                Text(
                  'چه بخشی را می‌خواهید شروع کنید؟ گرامر یا لغات؟',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontFamily: 'Outfit',
                        color: AppTheme.darkTextSub,
                      ),
                ).animate().fadeIn(delay: 200.ms),

                const SizedBox(height: 36),

                // Category options
                Expanded(
                  child: ListView(
                    physics: const BouncingScrollPhysics(),
                    children: [
                      // Grammar Option
                      _CategoryCard(
                        title: 'گرامر (Grammar)',
                        subtitle:
                            'آموزش گرامر از سطح A1 تا A2 به زبان مادری همراه با توضیح تفاوت‌ها و ۲ مثال کاربردی',
                        icon: Icons.menu_book_rounded,
                        accentGradient: const LinearGradient(
                          colors: [Color(0xFF8B5CF6), Color(0xFF6366F1)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        badgeText: 'A1 - A2 زبان مادری',
                        onTap: () {
                          context.push('/levels/$languageId');
                        },
                      ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.2, end: 0),

                      const SizedBox(height: 20),

                      // Vocabulary Option
                      _CategoryCard(
                        title: 'لغات (Vocabulary)',
                        subtitle:
                            'آموزش و مرور لغات کاربردی، اصطلاحات و کلمات سطح‌بندی شده',
                        icon: Icons.style_rounded,
                        accentGradient: const LinearGradient(
                          colors: [Color(0xFF06B6D4), Color(0xFF10B981)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        badgeText: 'کلمات و فلش‌کارت',
                        onTap: () {
                          context.push('/vocabulary/$languageId/A1');
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
  final VoidCallback onTap;

  const _CategoryCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.accentGradient,
    required this.badgeText,
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
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: accentGradient.colors.first.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                            color: accentGradient.colors.first.withOpacity(0.3)),
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
                      'ورود به این بخش',
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
