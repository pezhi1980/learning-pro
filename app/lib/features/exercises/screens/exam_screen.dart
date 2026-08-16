// lib/features/exercises/screens/exam_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/services/supabase_service.dart';

class ExamScreen extends StatefulWidget {
  final String languageId;
  final String levelId;
  final String? topicId;

  const ExamScreen({
    super.key,
    required this.languageId,
    required this.levelId,
    this.topicId,
  });

  @override
  State<ExamScreen> createState() => _ExamScreenState();
}

class _ExamScreenState extends State<ExamScreen> {
  List<Map<String, dynamic>> _examItems = [];
  bool _isLoading = true;
  int _currentIndex = 0;
  int _score = 0;
  bool _isAnswered = false;
  bool _isCorrect = false;

  // Input states for per-type interactions
  final TextEditingController _textController = TextEditingController();
  String? _selectedOption; // for MC
  List<String> _bankWords = []; // for sentence_order
  List<String> _userWords = []; // for sentence_order

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
    _loadExamExercises();
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _loadExamExercises() async {
    setState(() => _isLoading = true);
    try {
      final types = ['multiple_choice', 'fill_blank', 'sentence_order', 'error_correction', 'translation'];
      final List<Map<String, dynamic>> combined = [];

      for (final t in types) {
        final data = await SupabaseService.getExercises(
          languageId: widget.languageId,
          levelId: widget.levelId,
          type: t,
          nativeLanguage: 'fa',
          topicId: widget.topicId,
          limit: 2,
        );
        combined.addAll(data);
      }

      combined.shuffle();

      if (mounted) {
        setState(() {
          _examItems = combined;
          _isLoading = false;
          _resetCurrentState();
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _resetCurrentState() {
    _textController.clear();
    _selectedOption = null;
    _isAnswered = false;
    _isCorrect = false;

    if (_examItems.isNotEmpty && _currentIndex < _examItems.length) {
      final item = _examItems[_currentIndex];
      final type = item['type'] ?? 'multiple_choice';
      final content = item['content_json'] as Map<String, dynamic>? ?? {};

      if (type == 'sentence_order') {
        final target = (content['target_sentence'] as String? ?? '').trim();
        final clean = target.replaceAll(RegExp(r"[^\w\s']"), '').trim();
        final words = clean.split(RegExp(r'\s+'));
        _bankWords = List<String>.from(words)..shuffle();
        _userWords = [];
      }
    }
  }

  void _checkCurrentAnswer() {
    if (_isAnswered || _examItems.isEmpty) return;

    final item = _examItems[_currentIndex];
    final type = item['type'] ?? 'multiple_choice';
    final content = item['content_json'] as Map<String, dynamic>? ?? {};
    bool correct = false;

    if (type == 'multiple_choice') {
      final correctAns = content['correct_answer'] as String? ?? '';
      if (_selectedOption != null) {
        correct = _selectedOption!.trim() == correctAns.trim();
      }
    } else if (type == 'fill_blank') {
      final userInput = _textController.text.trim().toLowerCase();
      final correctAns = (content['correct_answer'] as String? ?? '').trim().toLowerCase();
      final acceptable = (content['acceptable_answers'] as List? ?? []).map((e) => e.toString().trim().toLowerCase()).toList();
      correct = userInput == correctAns || acceptable.contains(userInput);
    } else if (type == 'sentence_order') {
      final target = (content['target_sentence'] as String? ?? '').replaceAll(RegExp(r"[^\w\s']"), '').toLowerCase().trim();
      final userBuilt = _userWords.join(' ').replaceAll(RegExp(r"[^\w\s']"), '').toLowerCase().trim();
      correct = target == userBuilt;
    } else if (type == 'error_correction') {
      final userInput = _textController.text.trim().replaceAll(RegExp(r"[^\w\s']"), '').toLowerCase().replaceAll(RegExp(r'\s+'), ' ');
      final target = (content['correct_sentence'] as String? ?? '').replaceAll(RegExp(r"[^\w\s']"), '').toLowerCase().replaceAll(RegExp(r'\s+'), ' ');
      correct = userInput == target;
    } else if (type == 'translation') {
      final userInput = _textController.text.trim().replaceAll(RegExp(r"[^\w\s']"), '').toLowerCase().replaceAll(RegExp(r'\s+'), ' ');
      final target = (content['target_sentence'] as String? ?? '').replaceAll(RegExp(r"[^\w\s']"), '').toLowerCase().replaceAll(RegExp(r'\s+'), ' ');
      correct = userInput == target;
    }

    setState(() {
      _isAnswered = true;
      _isCorrect = correct;
      if (correct) _score++;
    });

    SupabaseService.updateProgress(
      languageId: widget.languageId,
      levelId: widget.levelId,
      topicId: widget.topicId,
      isCorrect: correct,
    );
  }

  void _onNext() {
    if (_currentIndex < _examItems.length - 1) {
      setState(() {
        _currentIndex++;
        _resetCurrentState();
      });
    } else {
      setState(() {
        _currentIndex++; // triggers result view
      });
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
    final total = _examItems.length;
    final isFinished = _currentIndex >= total;

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
          const Text('Comprehensive Exam 🎓', style: TextStyle(fontFamily: 'Outfit', fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.darkText)),
          const Spacer(),
          if (total > 0 && !isFinished)
            Text('${_currentIndex + 1}/$total', style: const TextStyle(fontFamily: 'Outfit', fontSize: 14, fontWeight: FontWeight.w600, color: AppTheme.darkTextSub)),
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_examItems.isEmpty) return const Center(child: Text('No exam exercises available.', style: TextStyle(color: AppTheme.darkTextSub)));
    if (_currentIndex >= _examItems.length) return _buildResultView();

    final item = _examItems[_currentIndex];
    final type = item['type'] ?? 'multiple_choice';

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildItemWidget(type, item),
          const SizedBox(height: 20),
          if (!_isAnswered)
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _checkCurrentAnswer,
                icon: const Icon(Icons.check_circle_rounded),
                label: const Text('Submit Answer'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _levelColor,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  textStyle: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w700),
                ),
              ),
            ),
          if (_isAnswered) ...[
            _buildFeedbackBox(item),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: _onNext,
                icon: const Icon(Icons.arrow_forward_rounded),
                label: Text(_currentIndex < _examItems.length - 1 ? 'Next Question' : 'View Results'),
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

  Widget _buildItemWidget(String type, Map<String, dynamic> item) {
    final content = item['content_json'] as Map<String, dynamic>? ?? {};

    if (type == 'multiple_choice') {
      final question = content['question'] as String? ?? '';
      final options = (content['options'] as List?)?.map((e) => e.toString()).toList() ?? [];

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(color: AppTheme.darkCard, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppTheme.darkCardBorder)),
            child: Text(question, style: const TextStyle(fontFamily: 'Outfit', fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.darkText)),
          ),
          const SizedBox(height: 16),
          ...options.asMap().entries.map((entry) {
            final opt = entry.value;
            final isSel = _selectedOption == opt;
            return Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: InkWell(
                onTap: _isAnswered ? null : () => setState(() => _selectedOption = opt),
                child: Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: isSel ? _levelColor.withOpacity(0.15) : AppTheme.darkCard,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: isSel ? _levelColor : AppTheme.darkCardBorder),
                  ),
                  child: Text(opt, style: const TextStyle(fontFamily: 'Outfit', fontSize: 16, color: AppTheme.darkText)),
                ),
              ),
            );
          }),
        ],
      );
    } else if (type == 'fill_blank') {
      final sentence = content['sentence'] as String? ?? '';
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(color: AppTheme.darkCard, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppTheme.darkCardBorder)),
            child: Text(sentence, style: const TextStyle(fontFamily: 'Outfit', fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.darkText)),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _textController,
            enabled: !_isAnswered,
            style: const TextStyle(fontFamily: 'Outfit', fontSize: 16, color: AppTheme.darkText),
            decoration: InputDecoration(
              hintText: 'Type answer...',
              filled: true,
              fillColor: AppTheme.darkCard,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
            ),
          ),
        ],
      );
    } else if (type == 'sentence_order') {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Reorder words to form a correct sentence:', style: TextStyle(fontFamily: 'Outfit', fontSize: 14, color: AppTheme.darkTextSub)),
          const SizedBox(height: 12),
          Container(
            minHeight: 60,
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: AppTheme.darkCard, borderRadius: BorderRadius.circular(14), border: Border.all(color: AppTheme.darkCardBorder)),
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _userWords.map((w) => ActionChip(label: Text(w), onPressed: _isAnswered ? null : () => setState(() { _userWords.remove(w); _bankWords.add(w); }))).toList(),
            ),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _bankWords.map((w) => ActionChip(label: Text(w), onPressed: _isAnswered ? null : () => setState(() { _bankWords.remove(w); _userWords.add(w); }))).toList(),
          ),
        ],
      );
    } else if (type == 'error_correction') {
      final incorrect = content['incorrect_sentence'] as String? ?? '';
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: AppTheme.colorError.withOpacity(0.12), borderRadius: BorderRadius.circular(14), border: Border.all(color: AppTheme.colorError.withOpacity(0.3))),
            child: Text(incorrect, style: const TextStyle(fontFamily: 'Outfit', fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.darkText, decoration: TextDecoration.lineThrough)),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _textController,
            enabled: !_isAnswered,
            style: const TextStyle(fontFamily: 'Outfit', fontSize: 16, color: AppTheme.darkText),
            decoration: InputDecoration(hintText: 'Type corrected sentence...', filled: true, fillColor: AppTheme.darkCard, border: OutlineInputBorder(borderRadius: BorderRadius.circular(14))),
          ),
        ],
      );
    } else { // translation
      final source = content['source_sentence'] as String? ?? '';
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Directionality(
            textDirection: TextDirection.rtl,
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(color: AppTheme.darkCard, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppTheme.darkCardBorder)),
              child: Text(source, style: const TextStyle(fontFamily: 'Outfit', fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.darkText)),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _textController,
            enabled: !_isAnswered,
            style: const TextStyle(fontFamily: 'Outfit', fontSize: 16, color: AppTheme.darkText),
            decoration: InputDecoration(hintText: 'Type English translation...', filled: true, fillColor: AppTheme.darkCard, border: OutlineInputBorder(borderRadius: BorderRadius.circular(14))),
          ),
        ],
      );
    }
  }

  Widget _buildFeedbackBox(Map<String, dynamic> item) {
    final content = item['content_json'] as Map<String, dynamic>? ?? {};
    final explanation = content['explanation'] as String? ?? '';

    return Container(
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
              Icon(_isCorrect ? Icons.check_circle_rounded : Icons.cancel_rounded, color: _isCorrect ? AppTheme.colorSuccess : AppTheme.colorError),
              const SizedBox(width: 8),
              Text(_isCorrect ? 'Correct!' : 'Incorrect', style: TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w700, color: _isCorrect ? AppTheme.colorSuccess : AppTheme.colorError)),
            ],
          ),
          if (explanation.isNotEmpty) ...[
            const SizedBox(height: 10),
            Directionality(
              textDirection: TextDirection.rtl,
              child: Text(explanation, textAlign: TextAlign.right, style: const TextStyle(fontFamily: 'Outfit', fontSize: 13, color: AppTheme.darkTextSub, height: 1.4)),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildResultView() {
    final total = _examItems.length;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 90,
              height: 90,
              decoration: BoxDecoration(color: _levelColor.withOpacity(0.15), shape: BoxShape.circle, border: Border.all(color: _levelColor, width: 3)),
              child: Center(child: Icon(Icons.emoji_events_rounded, size: 48, color: _levelColor)),
            ).animate().scale(duration: 500.ms, curve: Curves.elasticOut),
            const SizedBox(height: 24),
            const Text('Exam Complete! 🎓', style: TextStyle(fontFamily: 'Outfit', fontSize: 24, fontWeight: FontWeight.w800, color: AppTheme.darkText)),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              decoration: BoxDecoration(color: _levelColor.withOpacity(0.15), borderRadius: BorderRadius.circular(16), border: Border.all(color: _levelColor.withOpacity(0.3))),
              child: Text('Score: $_score / $total', style: TextStyle(fontFamily: 'Outfit', fontSize: 22, fontWeight: FontWeight.w800, color: _levelColor)),
            ),
            const SizedBox(height: 36),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: () {
                  setState(() {
                    _currentIndex = 0;
                    _score = 0;
                    _loadExamExercises();
                  });
                },
                icon: const Icon(Icons.replay_rounded),
                label: const Text('Retake Exam'),
                style: ElevatedButton.styleFrom(backgroundColor: _levelColor, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14))),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
