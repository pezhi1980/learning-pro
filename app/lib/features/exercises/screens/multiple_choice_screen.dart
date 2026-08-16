// lib/features/exercises/screens/multiple_choice_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:percent_indicator/linear_percent_indicator.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/services/supabase_service.dart';
import '../../../shared/widgets/loading_shimmer.dart';

enum ExerciseMode { practice, quiz }

class MultipleChoiceScreen extends StatefulWidget {
  final String languageId;
  final String levelId;
  final String? topicId;
  final ExerciseMode mode;

  const MultipleChoiceScreen({
    super.key,
    required this.languageId,
    required this.levelId,
    this.topicId,
    required this.mode,
  });

  @override
  State<MultipleChoiceScreen> createState() => _MultipleChoiceScreenState();
}

class _MultipleChoiceScreenState extends State<MultipleChoiceScreen> {
  List<Map<String, dynamic>> _exercises = [];
  bool _isLoading = true;
  String? _error;

  int _currentIndex = 0;
  String? _selectedOption;
  bool _isAnswered = false;
  int _score = 0;
  bool _isQuizComplete = false;

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
    _loadExercises();
  }

  Future<void> _loadExercises() async {
    setState(() {
      _isLoading = true;
      _error = null;
      _currentIndex = 0;
      _score = 0;
      _isQuizComplete = false;
      _selectedOption = null;
      _isAnswered = false;
    });

    try {
      final limitCount = widget.mode == ExerciseMode.quiz ? 10 : 5;
      final data = await SupabaseService.getExercises(
        languageId: widget.languageId,
        levelId: widget.levelId,
        type: 'multiple_choice',
        nativeLanguage: 'fa',
        topicId: widget.topicId,
        limit: limitCount,
      );

      if (mounted) {
        setState(() {
          _exercises = data;
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

  void _onOptionSelected(String option, String correctAnswer) {
    if (_isAnswered) return;

    final isCorrect = option.trim() == correctAnswer.trim();
    setState(() {
      _selectedOption = option;
      _isAnswered = true;
      if (isCorrect) _score++;

      // Adaptive Learning: If wrong in practice mode, dynamically append 2 targeted remedial questions
      if (widget.mode == ExerciseMode.practice && !isCorrect && _exercises.isNotEmpty) {
        final currentEx = _exercises[_currentIndex];
        final candidates = List<Map<String, dynamic>>.from(_exercises)
          ..remove(currentEx)
          ..shuffle();
        if (candidates.isNotEmpty) {
          final added = candidates.take(2).toList();
          _exercises.addAll(added);
        }
      }
    });

    // Update progress in DB (asynchronously)
    SupabaseService.updateProgress(
      languageId: widget.languageId,
      levelId: widget.levelId,
      topicId: widget.topicId,
      isCorrect: isCorrect,
    );
  }

  void _onNext() {
    if (_currentIndex < _exercises.length - 1) {
      setState(() {
        _currentIndex++;
        _selectedOption = null;
        _isAnswered = false;
      });
    } else {
      setState(() {
        _isQuizComplete = true;
      });
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
              _buildHeader(),
              Expanded(child: _buildBody()),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    final progress = _exercises.isEmpty ? 0.0 : (_currentIndex + 1) / _exercises.length;

    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 12, 20, 12),
      child: Column(
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
                    context.go('/grammar/${widget.languageId}/${widget.levelId}');
                  }
                },
              ),
              const SizedBox(width: 4),
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
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: _levelColor,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                widget.mode == ExerciseMode.quiz ? 'Quick Quiz' : 'Practice',
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.darkText,
                ),
              ),
              const Spacer(),
              if (_exercises.isNotEmpty && !_isQuizComplete)
                Text(
                  '${_currentIndex + 1}/${_exercises.length}',
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.darkTextSub,
                  ),
                ),
            ],
          ),
          if (_exercises.isNotEmpty && !_isQuizComplete) ...[
            const SizedBox(height: 10),
            LinearPercentIndicator(
              lineHeight: 6,
              percent: progress.clamp(0.0, 1.0),
              progressColor: _levelColor,
              backgroundColor: AppTheme.darkCardBorder,
              barRadius: const Radius.circular(3),
              padding: EdgeInsets.zero,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            LoadingShimmerCard(height: 120),
            const SizedBox(height: 20),
            LoadingShimmerCard(height: 60),
            const SizedBox(height: 12),
            LoadingShimmerCard(height: 60),
            const SizedBox(height: 12),
            LoadingShimmerCard(height: 60),
          ],
        ),
      );
    }

    if (_error != null) {
      return _buildErrorView();
    }

    if (_exercises.isEmpty) {
      return _buildEmptyView();
    }

    if (_isQuizComplete) {
      return _buildResultView();
    }

    final currentExercise = _exercises[_currentIndex];
    final contentJson = currentExercise['content_json'] as Map<String, dynamic>? ?? {};
    final question = contentJson['question'] as String? ?? '';
    final options = (contentJson['options'] as List?)?.map((e) => e.toString()).toList() ?? [];
    final correctAnswer = contentJson['correct_answer'] as String? ?? '';
    final explanation = contentJson['explanation'] as String? ?? '';

    return Column(
      children: [
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Question card
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.darkCard,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppTheme.darkCardBorder),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.help_outline_rounded, size: 18, color: _levelColor),
                          const SizedBox(width: 8),
                          Text(
                            'Select the correct answer',
                            style: TextStyle(
                              fontFamily: 'Outfit',
                              fontSize: 12,
                              color: _levelColor,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        question,
                        style: const TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.darkText,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ).animate().fadeIn(duration: 300.ms).slideY(begin: 0.05, end: 0),

                const SizedBox(height: 20),

                // Options list
                ...options.asMap().entries.map((entry) {
                  final index = entry.key;
                  final optionText = entry.value;
                  final prefix = ['A', 'B', 'C', 'D'][index % 4];

                  final isSelected = _selectedOption == optionText;
                  final isCorrectOption = optionText.trim() == correctAnswer.trim();

                  Color borderColor = AppTheme.darkCardBorder;
                  Color bgColor = AppTheme.darkCard;
                  Color textColor = AppTheme.darkText;
                  Widget? trailingIcon;

                  if (_isAnswered) {
                    if (isCorrectOption) {
                      borderColor = AppTheme.colorSuccess;
                      bgColor = AppTheme.colorSuccess.withOpacity(0.12);
                      textColor = AppTheme.colorSuccess;
                      trailingIcon = const Icon(Icons.check_circle_rounded, color: AppTheme.colorSuccess, size: 22);
                    } else if (isSelected) {
                      borderColor = AppTheme.colorError;
                      bgColor = AppTheme.colorError.withOpacity(0.12);
                      textColor = AppTheme.colorError;
                      trailingIcon = const Icon(Icons.cancel_rounded, color: AppTheme.colorError, size: 22);
                    }
                  }

                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: GestureDetector(
                      onTap: () => _onOptionSelected(optionText, correctAnswer),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                        decoration: BoxDecoration(
                          color: bgColor,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: borderColor, width: isSelected || ( _isAnswered && isCorrectOption) ? 2 : 1),
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 32,
                              height: 32,
                              decoration: BoxDecoration(
                                color: isSelected || (_isAnswered && isCorrectOption)
                                    ? borderColor.withOpacity(0.2)
                                    : AppTheme.darkBg,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Center(
                                child: Text(
                                  prefix,
                                  style: TextStyle(
                                    fontFamily: 'Outfit',
                                    fontSize: 14,
                                    fontWeight: FontWeight.w700,
                                    color: textColor,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Text(
                                optionText,
                                style: TextStyle(
                                  fontFamily: 'Outfit',
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: textColor,
                                ),
                              ),
                            ),
                            if (trailingIcon != null) trailingIcon,
                          ],
                        ),
                      ),
                    ),
                  ).animate().fadeIn(delay: (index * 60).ms, duration: 300.ms);
                }),

                // Explanation box (RTL supported for Farsi)
                if (_isAnswered && explanation.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Directionality(
                    textDirection: TextDirection.rtl,
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppTheme.accentAmber.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AppTheme.accentAmber.withOpacity(0.3)),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(Icons.lightbulb_rounded, size: 20, color: AppTheme.accentAmber),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              explanation,
                              textAlign: TextAlign.right,
                              style: const TextStyle(
                                fontFamily: 'Outfit',
                                fontSize: 13,
                                color: AppTheme.darkText,
                                height: 1.6,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ).animate().fadeIn(duration: 300.ms).slideY(begin: 0.1, end: 0),
                ],
              ],
            ),
          ),
        ),

        // Bottom CTA button
        if (_isAnswered)
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
            child: SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _onNext,
                icon: Icon(_currentIndex < _exercises.length - 1 ? Icons.arrow_forward_rounded : Icons.emoji_events_rounded),
                label: Text(_currentIndex < _exercises.length - 1 ? 'Next Question' : 'See Results'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _levelColor,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  textStyle: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w700),
                ),
              ),
            ),
          ).animate().fadeIn(duration: 200.ms),
      ],
    );
  }

  Widget _buildResultView() {
    final isQuiz = widget.mode == ExerciseMode.quiz;
    final total = _exercises.length;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 90,
              height: 90,
              decoration: BoxDecoration(
                color: _levelColor.withOpacity(0.15),
                shape: BoxShape.circle,
                border: Border.all(color: _levelColor, width: 3),
              ),
              child: Center(
                child: Icon(
                  isQuiz ? Icons.emoji_events_rounded : Icons.check_circle_rounded,
                  size: 48,
                  color: _levelColor,
                ),
              ),
            ).animate().scale(duration: 500.ms, curve: Curves.elasticOut),
            const SizedBox(height: 24),
            Text(
              isQuiz ? 'Quiz Complete! 🏆' : 'Practice Completed! 🎉',
              style: const TextStyle(
                fontFamily: 'Outfit',
                fontSize: 24,
                fontWeight: FontWeight.w800,
                color: AppTheme.darkText,
              ),
            ),
            const SizedBox(height: 8),
            if (isQuiz) ...[
              Container(
                margin: const EdgeInsets.symmetric(vertical: 12),
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                decoration: BoxDecoration(
                  color: _levelColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: _levelColor.withOpacity(0.3)),
                ),
                child: Text(
                  'Score: $_score / $total',
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: _levelColor,
                  ),
                ),
              ),
              Text(
                'You scored $_score out of $total on this quiz.',
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 14,
                  color: AppTheme.darkTextSub,
                  height: 1.5,
                ),
              ),
            ] else ...[
              Text(
                'Great job practicing! You have practiced $total exercises and reinforced your understanding of this topic.',
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontFamily: 'Outfit',
                  fontSize: 14,
                  color: AppTheme.darkTextSub,
                  height: 1.5,
                ),
              ),
            ],
            const SizedBox(height: 36),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _loadExercises,
                icon: const Icon(Icons.replay_rounded),
                label: Text(isQuiz ? 'Retake Quiz' : 'Practice Again'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _levelColor,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  textStyle: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w700),
                ),
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: OutlinedButton.icon(
                onPressed: () {
                  if (context.canPop()) {
                    context.pop();
                  } else {
                    context.go('/grammar/${widget.languageId}/${widget.levelId}');
                  }
                },
                icon: const Icon(Icons.arrow_back_rounded),
                label: const Text('Back to Grammar'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppTheme.darkText,
                  side: const BorderSide(color: AppTheme.darkCardBorder),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  textStyle: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.quiz_outlined, size: 64, color: _levelColor.withOpacity(0.5)),
            const SizedBox(height: 20),
            const Text('Quiz Coming Soon',
                style: TextStyle(fontFamily: 'Outfit', fontSize: 20, fontWeight: FontWeight.w700, color: AppTheme.darkText)),
            const SizedBox(height: 8),
            const Text('Exercises for this topic are being generated.',
                textAlign: TextAlign.center, style: TextStyle(fontSize: 14, color: AppTheme.darkTextSub)),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                if (context.canPop()) {
                  context.pop();
                } else {
                  context.go('/grammar/${widget.languageId}/${widget.levelId}');
                }
              },
              icon: const Icon(Icons.arrow_back_rounded),
              label: const Text('Back to Grammar'),
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

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.wifi_off_rounded, size: 48, color: AppTheme.colorError),
          const SizedBox(height: 16),
          const Text('Could not load quiz', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: AppTheme.darkText)),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _loadExercises,
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('Retry'),
            style: ElevatedButton.styleFrom(backgroundColor: _levelColor, foregroundColor: Colors.white),
          ),
        ],
      ),
    );
  }
}
