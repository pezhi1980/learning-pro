// lib/features/exercises/screens/error_correction_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/services/supabase_service.dart';

class ErrorCorrectionScreen extends StatefulWidget {
  final String languageId;
  final String levelId;
  final String? topicId;

  const ErrorCorrectionScreen({
    super.key,
    required this.languageId,
    required this.levelId,
    this.topicId,
  });

  @override
  State<ErrorCorrectionScreen> createState() => _ErrorCorrectionScreenState();
}

class _ErrorCorrectionScreenState extends State<ErrorCorrectionScreen> {
  List<Map<String, dynamic>> _exercises = [];
  bool _isLoading = true;

  int _currentIndex = 0;
  String? _selectedOption;
  bool _isAnswered = false;

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
    setState(() => _isLoading = true);
    try {
      final rawData = await SupabaseService.getExercises(
        languageId: widget.languageId,
        levelId: widget.levelId,
        type: 'multiple_choice',
        nativeLanguage: 'fa',
        topicId: widget.topicId,
        limit: 5,
      );

      if (mounted) {
        setState(() {
          _exercises = rawData;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _onOptionSelected(String option, String correctAnswer) {
    if (_isAnswered) return;

    final isCorrect = option.trim() == correctAnswer.trim();
    setState(() {
      _selectedOption = option;
      _isAnswered = true;

      // Adaptive Learning: If wrong, dynamically append 2 targeted remedial exercises
      if (!isCorrect && _exercises.isNotEmpty) {
        final currentEx = _exercises[_currentIndex];
        final candidates = List<Map<String, dynamic>>.from(_exercises)..remove(currentEx)..shuffle();
        if (candidates.isNotEmpty) {
          _exercises.addAll(candidates.take(2));
        }
      }
    });

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
      if (context.canPop()) {
        context.pop();
      } else {
        context.go('/grammar/${widget.languageId}/${widget.levelId}');
      }
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
    return Padding(
      padding: const EdgeInsets.all(16),
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
            child: Text(widget.levelId, style: TextStyle(fontFamily: 'Outfit', fontSize: 12, fontWeight: FontWeight.w700, color: _levelColor)),
          ),
          const SizedBox(width: 8),
          const Text('Error Correction 🔍', style: TextStyle(fontFamily: 'Outfit', fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.darkText)),
          const Spacer(),
          if (_exercises.isNotEmpty)
            Text('${_currentIndex + 1}/${_exercises.length}', style: const TextStyle(fontFamily: 'Outfit', fontSize: 14, fontWeight: FontWeight.w600, color: AppTheme.darkTextSub)),
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_exercises.isEmpty) return const Center(child: Text('No error correction exercises available.', style: TextStyle(color: AppTheme.darkTextSub)));

    final ex = _exercises[_currentIndex];
    final content = ex['content_json'] as Map<String, dynamic>? ?? {};
    final question = content['question'] as String? ?? '';
    final options = (content['options'] as List?)?.map((e) => e.toString()).toList() ?? [];
    final correctAnswer = content['correct_answer'] as String? ?? '';
    final explanation = content['explanation'] as String? ?? '';

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: AppTheme.darkCard,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.darkCardBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.search_rounded, size: 18, color: AppTheme.accentAmber),
                    SizedBox(width: 8),
                    Text('Spot and correct the mistake:', style: TextStyle(fontFamily: 'Outfit', fontSize: 12, color: AppTheme.accentAmber, fontWeight: FontWeight.w600)),
                  ],
                ),
                const SizedBox(height: 12),
                Text(question, style: const TextStyle(fontFamily: 'Outfit', fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.darkText, height: 1.4)),
              ],
            ),
          ).animate().fadeIn(duration: 300.ms),

          const SizedBox(height: 20),

          ...options.asMap().entries.map((entry) {
            final idx = entry.key;
            final optionText = entry.value;
            final isSelected = _selectedOption == optionText;
            final isCorrectOption = optionText.trim() == correctAnswer.trim();

            Color borderColor = AppTheme.darkCardBorder;
            Color bgColor = AppTheme.darkCard;

            if (_isAnswered) {
              if (isCorrectOption) {
                borderColor = AppTheme.colorSuccess;
                bgColor = AppTheme.colorSuccess.withOpacity(0.12);
              } else if (isSelected) {
                borderColor = AppTheme.colorError;
                bgColor = AppTheme.colorError.withOpacity(0.12);
              }
            }

            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: GestureDetector(
                onTap: () => _onOptionSelected(optionText, correctAnswer),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: bgColor,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: borderColor, width: isSelected || (_isAnswered && isCorrectOption) ? 2 : 1),
                  ),
                  child: Row(
                    children: [
                      Text(['A', 'B', 'C', 'D'][idx % 4], style: TextStyle(fontFamily: 'Outfit', fontWeight: FontWeight.w700, color: _levelColor)),
                      const SizedBox(width: 14),
                      Expanded(child: Text(optionText, style: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w600, color: AppTheme.darkText))),
                    ],
                  ),
                ),
              ),
            );
          }),

          const Spacer(),

          if (_isAnswered && explanation.isNotEmpty) ...[
            Directionality(
              textDirection: TextDirection.rtl,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.accentAmber.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.accentAmber.withOpacity(0.4)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.lightbulb_rounded, color: AppTheme.accentAmber),
                    const SizedBox(width: 10),
                    Expanded(child: Text(explanation, textAlign: TextAlign.right, style: const TextStyle(fontFamily: 'Outfit', fontSize: 13, color: AppTheme.darkText, height: 1.5))),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],

          if (_isAnswered)
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _onNext,
                icon: const Icon(Icons.arrow_forward_rounded),
                label: const Text('Next Correction'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _levelColor,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  textStyle: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w700),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
