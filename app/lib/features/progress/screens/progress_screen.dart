// lib/features/progress/screens/progress_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/services/supabase_service.dart';
import '../../../core/utils/localization_helper.dart';
import '../../../shared/widgets/loading_shimmer.dart';

class ProgressScreen extends StatefulWidget {
  final String languageId;
  final String levelId;

  const ProgressScreen({
    super.key,
    this.languageId = 'en',
    this.levelId = 'A1',
  });

  @override
  State<ProgressScreen> createState() => _ProgressScreenState();
}

class _ProgressScreenState extends State<ProgressScreen> {
  Map<String, dynamic>? _profile;
  List<Map<String, dynamic>> _weakTopics = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadProgressData();
  }

  Future<void> _loadProgressData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final profileData = await SupabaseService.getProfile();
      final weakTopicsData = await SupabaseService.getWeakTopics(
        languageId: widget.languageId,
        levelId: widget.levelId,
      );

      if (mounted) {
        setState(() {
          _profile = profileData;
          _weakTopics = weakTopicsData;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded,
              color: AppTheme.darkTextSub, size: 20),
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/category-select/${widget.languageId}');
            }
          },
        ),
        title: Text(
          LocalizationHelper.tr('learner_progress', lang: LocalizationHelper.currentLang),
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: AppTheme.darkText,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: AppTheme.darkTextSub),
            onPressed: _loadProgressData,
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.darkBgGradient),
        child: SafeArea(
          child: _buildBody(),
        ),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const LoadingShimmerCard(height: 140),
            const SizedBox(height: 16),
            const LoadingShimmerCard(height: 200),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded,
                size: 48, color: AppTheme.colorError),
            const SizedBox(height: 16),
            Text(
              LocalizationHelper.tr('error_loading', lang: LocalizationHelper.currentLang),
              style: TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.darkText),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _loadProgressData,
              icon: const Icon(Icons.refresh_rounded),
              label: Text(LocalizationHelper.tr('try_again', lang: LocalizationHelper.currentLang)),
            ),
          ],
        ),
      );
    }

    final firstName = _profile?['first_name'] as String? ?? LocalizationHelper.tr('user', lang: LocalizationHelper.currentLang);
    final lastName = _profile?['last_name'] as String? ?? '';
    final nativeLang = _profile?['native_language'] as String? ?? 'fa';
    final role = _profile?['role'] as String? ?? 'learner';

    return ListView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.all(20),
      children: [
        // Profile Card
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppTheme.darkCard,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.darkCardBorder),
          ),
          child: Row(
            children: [
              CircleAvatar(
                radius: 30,
                backgroundColor: AppTheme.primaryPurple.withOpacity(0.2),
                child: Text(
                  firstName.isNotEmpty ? firstName[0].toUpperCase() : 'U',
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 24,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.primaryPurple,
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$firstName $lastName',
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.darkText,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${LocalizationHelper.tr('native_language_label', lang: LocalizationHelper.currentLang)}: ${LocalizationHelper.nativeLanguageNames[nativeLang] ?? nativeLang} · نقش: $role',
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 13,
                        color: AppTheme.darkTextSub,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ).animate().fadeIn(duration: 300.ms),

        const SizedBox(height: 20),

        // Statistics Overview
        Row(
          children: [
            Expanded(
              child: _StatCard(
                title: LocalizationHelper.tr('active_level', lang: LocalizationHelper.currentLang),
                value: widget.levelId,
                icon: Icons.military_tech_rounded,
                color: const Color(0xFF10B981),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _StatCard(
                title: LocalizationHelper.tr('target_language', lang: LocalizationHelper.currentLang),
                value: widget.languageId == 'en' ? LocalizationHelper.tr('english_lang', lang: LocalizationHelper.currentLang) : widget.languageId.toUpperCase(),
                icon: Icons.language_rounded,
                color: const Color(0xFF06B6D4),
              ),
            ),
          ],
        ).animate().fadeIn(delay: 150.ms),

        const SizedBox(height: 24),

        // Weak topics / Review Recommendations
        Text(
          LocalizationHelper.tr('topics_to_review', lang: LocalizationHelper.currentLang),
          style: TextStyle(
            fontFamily: 'Outfit',
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppTheme.darkText,
          ),
        ).animate().fadeIn(delay: 250.ms),

        const SizedBox(height: 12),

        if (_weakTopics.isEmpty)
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppTheme.darkCard,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.darkCardBorder),
            ),
            child: Row(
              children: [
                const Icon(Icons.check_circle_outline_rounded,
                    color: Color(0xFF10B981), size: 24),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    LocalizationHelper.tr('no_weaknesses', lang: LocalizationHelper.currentLang),
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 14,
                      color: AppTheme.darkTextSub,
                    ),
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(delay: 300.ms)
        else
          ..._weakTopics.map(
            (topic) => Container(
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppTheme.darkCard,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppTheme.darkCardBorder),
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_rounded,
                      color: AppTheme.accentAmber, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      topic['title']?.toString() ?? 'Topic',
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 14,
                        color: AppTheme.darkText,
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      context.push(
                        '/grammar-detail/${widget.languageId}/${widget.levelId}/${topic['topic_id'] ?? topic['id']}',
                      );
                    },
                    child: Text(LocalizationHelper.tr('practice_again', lang: LocalizationHelper.currentLang)),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.darkCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.darkCardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 12),
          Text(
            title,
            style: const TextStyle(
              fontFamily: 'Outfit',
              fontSize: 12,
              color: AppTheme.darkTextSub,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontFamily: 'Outfit',
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
