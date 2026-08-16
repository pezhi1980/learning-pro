// lib/features/exercises/screens/fill_blank_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/services/supabase_service.dart';

class FillBlankScreen extends StatefulWidget {
  final String languageId;
  final String levelId;
  final String? topicId;

  const FillBlankScreen({
    super.key,
    required this.languageId,
    required this.levelId,
    this.topicId,
  });

  @override
  State<FillBlankScreen> createState() => _FillBlankScreenState();
}

class _FillBlankScreenState extends State<FillBlankScreen> {
  List<Map<String, dynamic>> _exercises = [];
  bool _isLoading = true;
  int _currentIndex = 0;
  bool _isAnswered = false;
  bool _isCorrect = false;

  final TextEditingController _textController = TextEditingController();

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

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _loadExercises() async {
    setState(() => _isLoading = true);
    try {
      final rawData = await SupabaseService.getExercises(
        languageId: widget.languageId,
        levelId: widget.levelId,
        type: 'fill_blank',
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

  void _submitAnswer(String correctAnswer, List<dynamic> acceptableAnswers) {
    if (_isAnswered) return;

    final userInput = _textController.text.trim().toLowerCase();
    if (userInput.isEmpty) return;

    final cleanCorrect = correctAnswer.trim().toLowerCase();
    final cleanAcceptable = acceptableAnswers.map((e) => e.toString().trim().toLowerCase()).toList();

    final isCorrect = userInput == cleanCorrect || cleanAcceptable.contains(userInput);

    setState(() {
      _isAnswered = true;
      _isCorrect = isCorrect;

      // Adaptive Learning: Append 2 extra practice items on wrong answer
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
        _isAnswered = false;
        _isCorrect = false;
        _textController.clear();
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
      backgroundColor: AppTheme.darkBackground,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            Expanded(child: _buildBody()),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      decoration: const BoxDecoration(
        color: AppTheme.darkSurface,
        border: Border(bottom: BorderSide(color: AppTheme.darkCardBorder)),
      ),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_rounded, color: AppTheme.darkText),
            onPressed: () => context.pop(),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _levelColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(widget.levelId, style: TextStyle(fontFamily: 'Outfit', fontSize: 12, fontWeight: FontWeight.w700, color: _levelColor)),
          ),
          const SizedBox(width: 8),
          const Text('Fill in the Blank ✏️', style: TextStyle(fontFamily: 'Outfit', fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.darkText)),
          const Spacer(),
          if (_exercises.isNotEmpty)
            Text('${_currentIndex + 1}/${_exercises.length}', style: const TextStyle(fontFamily: 'Outfit', fontSize: 14, fontWeight: FontWeight.w600, color: AppTheme.darkTextSub)),
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_exercises.isEmpty) return const Center(child: Text('No fill-in-the-blank exercises available.', style: TextStyle(color: AppTheme.darkTextSub)));

    final ex = _exercises[_currentIndex];
    final content = ex['content_json'] as Map<String, dynamic>? ?? {};
    final sentence = content['sentence'] as String? ?? '';
    final correctAnswer = content['correct_answer'] as String? ?? '';
    final acceptableAnswers = content['acceptable_answers'] as List? ?? [];
    final explanation = content['explanation'] as String? ?? '';

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
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
                const Row(
                  children: [
                    Icon(Icons.edit_note_rounded, size: 20, color: AppTheme.primaryPurple),
                    SizedBox(width: 8),
                    Text('Fill in the missing word:', style: TextStyle(fontFamily: 'Outfit', fontSize: 13, color: AppTheme.primaryPurple, fontWeight: FontWeight.w600)),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  sentence,
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.darkText,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(duration: 300.ms),

          const SizedBox(height: 24),

          TextField(
            controller: _textController,
            enabled: !_isAnswered,
            style: const TextStyle(fontFamily: 'Outfit', fontSize: 16, color: AppTheme.darkText),
            decoration: InputDecoration(
              hintText: 'Type your answer here...',
              hintStyle: const TextStyle(color: AppTheme.darkTextSub),
              filled: true,
              fillColor: AppTheme.darkCard,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: const BorderSide(color: AppTheme.darkCardBorder),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(color: _levelColor, width: 2),
              ),
            ),
            onSubmitted: (_) => _submitAnswer(correctAnswer, acceptableAnswers),
          ),

          const SizedBox(height: 16),

          if (!_isAnswered)
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: () => _submitAnswer(correctAnswer, acceptableAnswers),
                icon: const Icon(Icons.check_circle_rounded),
                label: const Text('Check Answer'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _levelColor,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  textStyle: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w700),
                ),
              ),
            ),

          if (_isAnswered) ...[
            const SizedBox(height: 20),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _isCorrect ? AppTheme.colorSuccess.withOpacity(0.12) : AppTheme.colorError.withOpacity(0.12),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: _isCorrect ? AppTheme.colorSuccess : AppTheme.colorError),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        _isCorrect ? Icons.check_circle_rounded : Icons.cancel_rounded,
                        color: _isCorrect ? AppTheme.colorSuccess : AppTheme.colorError,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _isCorrect ? 'Correct!' : 'Incorrect',
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: _isCorrect ? AppTheme.colorSuccess : AppTheme.colorError,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Correct Answer: $correctAnswer',
                    style: const TextStyle(fontFamily: 'Outfit', fontSize: 15, fontWeight: FontWeight.w600, color: AppTheme.darkText),
                  ),
                  if (explanation.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Directionality(
                      textDirection: TextDirection.rtl,
                      child: Text(
                        explanation,
                        textAlign: TextAlign.right,
                        style: const TextStyle(fontFamily: 'Outfit', fontSize: 13, color: AppTheme.darkTextSub, height: 1.4),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _onNext,
                icon: const Icon(Icons.arrow_forward_rounded),
                label: const Text('Next Question'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _levelColor,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  textStyle: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w700),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
