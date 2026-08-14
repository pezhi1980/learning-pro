// lib/features/exercises/screens/exercise_hub_screen.dart

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import 'multiple_choice_screen.dart';
import 'sentence_order_screen.dart';
import 'error_correction_screen.dart';

class ExerciseHubScreen extends StatefulWidget {
  final String languageId;
  final String levelId;
  final String? topicId;

  const ExerciseHubScreen({
    super.key,
    required this.languageId,
    required this.levelId,
    this.topicId,
  });

  @override
  State<ExerciseHubScreen> createState() => _ExerciseHubScreenState();
}

class _ExerciseHubScreenState extends State<ExerciseHubScreen> {
  late final PageController _pageController;
  int _currentPage = 0;

  static const Map<String, Color> _levelColors = {
    'A1': Color(0xFF10B981),
    'A2': Color(0xFF06B6D4),
    'B1': Color(0xFF3B82F6),
    'B2': Color(0xFF8B5CF6),
    'C1': Color(0xFFEC4899),
    'C2': Color(0xFFF59E0B),
  };

  Color get _levelColor => _levelColors[widget.levelId] ?? AppTheme.primaryPurple;

  final List<Map<String, String>> _modes = [
    {'title': 'Multiple Choice', 'icon': '📝'},
    {'title': 'Sentence Ordering', 'icon': '🧩'},
    {'title': 'Error Correction', 'icon': '🔍'},
  ];

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _nextPage() {
    if (_currentPage < _modes.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 350),
        curve: Curves.easeInOut,
      );
    } else {
      if (context.canPop()) {
        context.pop();
      } else {
        context.go('/grammar/${widget.languageId}/${widget.levelId}');
      }
    }
  }

  void _prevPage() {
    if (_currentPage > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 350),
        curve: Curves.easeInOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentMode = _modes[_currentPage];

    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.darkBgGradient),
        child: SafeArea(
          child: Column(
            children: [
              // Top Header with Topic / Mode Indicator
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios_new_rounded, color: AppTheme.darkTextSub, size: 20),
                      onPressed: () => context.canPop() ? context.pop() : context.go('/grammar/${widget.languageId}/${widget.levelId}'),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: _levelColor.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: _levelColor.withOpacity(0.4)),
                      ),
                      child: Text(
                        '${widget.levelId} Practice',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: _levelColor,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        '${currentMode['icon']} ${currentMode['title']}',
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.darkText,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Text(
                      'Page ${_currentPage + 1}/${_modes.length}',
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.darkTextSub,
                      ),
                    ),
                  ],
                ),
              ),

              // Multipage View of Practice Modes
              Expanded(
                child: PageView(
                  controller: _pageController,
                  onPageChanged: (index) {
                    setState(() => _currentPage = index);
                  },
                  children: [
                    MultipleChoiceScreen(
                      languageId: widget.languageId,
                      levelId: widget.levelId,
                      topicId: widget.topicId,
                    ),
                    SentenceOrderScreen(
                      languageId: widget.languageId,
                      levelId: widget.levelId,
                      topicId: widget.topicId,
                    ),
                    ErrorCorrectionScreen(
                      languageId: widget.languageId,
                      levelId: widget.levelId,
                      topicId: widget.topicId,
                    ),
                  ],
                ),
              ),

              // Bottom Navigation Bar with Arrow Button
              Container(
                padding: const EdgeInsets.fromLTRB(20, 10, 20, 16),
                decoration: const BoxDecoration(
                  color: AppTheme.darkSurface,
                  border: Border(top: BorderSide(color: AppTheme.darkCardBorder)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    if (_currentPage > 0)
                      OutlinedButton.icon(
                        onPressed: _prevPage,
                        icon: const Icon(Icons.arrow_back_rounded, size: 18),
                        label: const Text('Previous Mode'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: AppTheme.darkTextSub,
                          side: const BorderSide(color: AppTheme.darkCardBorder),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                      )
                    else
                      const SizedBox.shrink(),

                    ElevatedButton.icon(
                      onPressed: _nextPage,
                      icon: Icon(_currentPage < _modes.length - 1 ? Icons.arrow_forward_rounded : Icons.check_circle_rounded, size: 18),
                      label: Text(_currentPage < _modes.length - 1 ? 'Next Practice Mode' : 'Complete Practice'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _levelColor,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        textStyle: const TextStyle(fontFamily: 'Outfit', fontSize: 14, fontWeight: FontWeight.w700),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
