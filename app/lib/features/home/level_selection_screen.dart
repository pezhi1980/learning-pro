import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/utils/router.dart';

class LevelSelectionScreen extends StatefulWidget {
  final String languageId;
  const LevelSelectionScreen({super.key, required this.languageId});

  @override
  State<LevelSelectionScreen> createState() => _LevelSelectionScreenState();
}

class _LevelSelectionScreenState extends State<LevelSelectionScreen> {
  final List<Map<String, dynamic>> _levels = [
    {
      'id': 'A1',
      'title': 'Beginner (A1)',
      'description': 'Start from scratch. Learn basic phrases and greetings.',
      'icon': Icons.egg_alt_rounded,
      'color': const Color(0xFF10B981), // Emerald
    },
    {
      'id': 'A2',
      'title': 'Elementary (A2)',
      'description': 'Understand frequently used expressions in daily life.',
      'icon': Icons.cruelty_free_rounded,
      'color': const Color(0xFF0D9488), // Teal
    },
    {
      'id': 'B1',
      'title': 'Intermediate (B1)',
      'description': 'Deal with most situations likely to arise while travelling.',
      'icon': Icons.directions_run_rounded,
      'color': const Color(0xFF3B82F6), // Blue
    },
    {
      'id': 'B2',
      'title': 'Upper Intermediate (B2)',
      'description': 'Understand the main ideas of complex text.',
      'icon': Icons.flight_takeoff_rounded,
      'color': const Color(0xFF8B5CF6), // Purple
    },
    {
      'id': 'C1',
      'title': 'Advanced (C1)',
      'description': 'Express ideas fluently and spontaneously.',
      'icon': Icons.psychology_rounded,
      'color': const Color(0xFFF59E0B), // Amber
    },
    {
      'id': 'C2',
      'title': 'Mastery (C2)',
      'description': 'Understand with ease virtually everything heard or read.',
      'icon': Icons.diamond_rounded,
      'color': const Color(0xFFEF4444), // Red
    },
  ];

  String? _selectedLevelId;

  String _getLanguageName() {
    switch (widget.languageId) {
      case 'en': return 'English';
      case 'fr': return 'French';
      case 'de': return 'German';
      case 'it': return 'Italian';
      case 'es': return 'Spanish';
      default: return 'Language';
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 16),
              
              // Back Button & Header
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: () => context.pop(),
                      icon: const Icon(Icons.arrow_back_ios_new_rounded, color: AppTheme.darkText),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryPurple.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppTheme.primaryPurple.withOpacity(0.3)),
                      ),
                      child: Text(
                        _getLanguageName(),
                        style: const TextStyle(
                          color: AppTheme.primaryPurple,
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                      ),
                    ).animate().fadeIn().slideX(begin: 0.2, end: 0),
                  ],
                ),
              ),
              
              const SizedBox(height: 24),
              
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Choose your level',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                            color: AppTheme.darkText,
                            fontWeight: FontWeight.w700,
                          ),
                    ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2, end: 0),
                    const SizedBox(height: 8),
                    Text(
                      'Select your current proficiency level',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: AppTheme.darkTextSub,
                          ),
                    ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.2, end: 0),
                  ],
                ),
              ),
              
              const SizedBox(height: 32),
              
              Expanded(
                child: ListView.separated(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                  physics: const BouncingScrollPhysics(),
                  itemCount: _levels.length,
                  separatorBuilder: (context, index) => const SizedBox(height: 16),
                  itemBuilder: (context, index) {
                    final level = _levels[index];
                    final isSelected = _selectedLevelId == level['id'];
                    
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedLevelId = level['id'];
                        });
                      },
                      child: AnimatedContainer(
                        duration: AppTheme.animNormal,
                        curve: Curves.easeOutCubic,
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: isSelected ? level['color'].withOpacity(0.1) : AppTheme.darkCard,
                          borderRadius: BorderRadius.circular(24),
                          border: Border.all(
                            color: isSelected ? level['color'] : AppTheme.darkCardBorder,
                            width: isSelected ? 2 : 1,
                          ),
                          boxShadow: isSelected
                              ? [
                                  BoxShadow(
                                    color: level['color'].withOpacity(0.15),
                                    blurRadius: 20,
                                    spreadRadius: 0,
                                  )
                                ]
                              : [],
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 56,
                              height: 56,
                              decoration: BoxDecoration(
                                color: isSelected ? level['color'] : AppTheme.darkBg,
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(
                                  color: isSelected ? Colors.transparent : AppTheme.darkCardBorder,
                                ),
                              ),
                              child: Icon(
                                level['icon'],
                                color: isSelected ? Colors.white : level['color'],
                                size: 28,
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    level['title'],
                                    style: TextStyle(
                                      fontFamily: 'Outfit',
                                      fontSize: 18,
                                      fontWeight: FontWeight.w700,
                                      color: AppTheme.darkText,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    level['description'],
                                    style: TextStyle(
                                      fontFamily: 'Outfit',
                                      fontSize: 13,
                                      color: AppTheme.darkTextSub,
                                      height: 1.4,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 16),
                            Container(
                              width: 24,
                              height: 24,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: isSelected ? level['color'] : Colors.transparent,
                                border: Border.all(
                                  color: isSelected ? level['color'] : AppTheme.darkTextSub.withOpacity(0.5),
                                  width: 2,
                                ),
                              ),
                              child: isSelected
                                  ? const Icon(Icons.check_rounded, color: Colors.white, size: 16)
                                  : null,
                            ).animate(target: isSelected ? 1 : 0).scale(),
                          ],
                        ),
                      ),
                    ).animate().fadeIn(delay: Duration(milliseconds: 100 * index)).slideX(begin: 0.1, end: 0);
                  },
                ),
              ),
              
              _buildBottomButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBottomButton() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppTheme.darkBg,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 30,
            offset: const Offset(0, -10),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton(
            onPressed: _selectedLevelId == null
                ? null
                : () {
                    // Navigate to Grammar/Exercises Hub
                    context.push(AppRoutes.grammarList
                        .replaceFirst(':languageId', widget.languageId)
                        .replaceFirst(':levelId', _selectedLevelId!));
                  },
            style: ElevatedButton.styleFrom(
              backgroundColor: _selectedLevelId != null ? AppTheme.primaryPurple : AppTheme.darkCard,
              foregroundColor: _selectedLevelId != null ? Colors.white : AppTheme.darkTextSub,
              disabledBackgroundColor: AppTheme.darkCard,
              disabledForegroundColor: AppTheme.darkTextSub,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              elevation: _selectedLevelId != null ? 8 : 0,
              shadowColor: AppTheme.primaryPurple.withOpacity(0.5),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  'Start Learning',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(width: 8),
                const Icon(Icons.rocket_launch_rounded, size: 20),
              ],
            ),
          ),
        ),
      ),
    ).animate().slideY(begin: 1, end: 0, duration: 500.ms, curve: Curves.easeOutCubic);
  }
}
