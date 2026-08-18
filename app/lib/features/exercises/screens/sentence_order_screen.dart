// lib/features/exercises/screens/sentence_order_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/services/supabase_service.dart';
import '../../../core/utils/localization_helper.dart';

class SentenceOrderScreen extends StatefulWidget {
  final String languageId;
  final String levelId;
  final String? topicId;

  const SentenceOrderScreen({
    super.key,
    required this.languageId,
    required this.levelId,
    this.topicId,
  });

  @override
  State<SentenceOrderScreen> createState() => _SentenceOrderScreenState();
}

class _SentenceOrderScreenState extends State<SentenceOrderScreen> {
  // Built dynamically from DB exercises
  List<Map<String, dynamic>> _items = [];
  bool _isLoading = true;
  int _currentIndex = 0;

  List<String> _bankWords = [];
  List<String> _userWords = [];
  bool _isAnswered = false;
  bool _isCorrect = false;

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
        type: 'sentence_order',
        nativeLanguage: await LocalizationHelper.getSelectedExplanationLanguage(),
        topicId: widget.topicId,
        limit: 5,
      );

      final List<Map<String, dynamic>> parsed = [];

      for (final row in rawData) {
        final content = row['content_json'] as Map<String, dynamic>? ?? {};
        final fullSentence = (content['target_sentence'] as String? ?? '').trim();
        final explanation = content['explanation'] as String? ?? '';

        if (fullSentence.isNotEmpty) {
          final cleanText = fullSentence.replaceAll(RegExp(r"[^\w\s']"), '').trim();
          final words = cleanText.split(RegExp(r'\s+'));

          if (words.length >= 2) {
            final scrambled = List<String>.from(words)..shuffle();
            parsed.add({
              'words': scrambled,
              'target_sentence': cleanText.isNotEmpty ? cleanText : fullSentence,
              'raw_sentence': fullSentence,
              'explanation': explanation,
            });
          }
        }
      }

      if (mounted) {
        setState(() {
          _items = parsed;
          _isLoading = false;
          _resetCurrentItem();
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _resetCurrentItem() {
    if (_items.isEmpty || _currentIndex >= _items.length) return;
    final item = _items[_currentIndex];
    setState(() {
      _bankWords = List<String>.from(item['words']);
      _userWords = [];
      _isAnswered = false;
      _isCorrect = false;
    });
  }

  void _selectWord(String word) {
    if (_isAnswered) return;
    setState(() {
      _bankWords.remove(word);
      _userWords.add(word);
    });
  }

  void _deselectWord(String word) {
    if (_isAnswered) return;
    setState(() {
      _userWords.remove(word);
      _bankWords.add(word);
    });
  }

  void _checkAnswer() {
    if (_isAnswered || _userWords.isEmpty) return;

    final target = (_items[_currentIndex]['target_sentence'] as String).toLowerCase().trim();
    final userBuilt = _userWords.join(' ').toLowerCase().trim();
    final correct = target == userBuilt;

    setState(() {
      _isAnswered = true;
      _isCorrect = correct;

      // Adaptive Learning: Append 2 extra practice items on wrong answer
      if (!correct && _items.isNotEmpty) {
        final current = _items[_currentIndex];
        final candidates = List<Map<String, dynamic>>.from(_items)..remove(current)..shuffle();
        if (candidates.isNotEmpty) {
          _items.addAll(candidates.take(2));
        }
      }
    });
  }

  void _onNext() {
    if (_currentIndex < _items.length - 1) {
      setState(() {
        _currentIndex++;
        _resetCurrentItem();
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
          const Text('Sentence Order ðŸ§©', style: TextStyle(fontFamily: 'Outfit', fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.darkText)),
          const Spacer(),
          if (_items.isNotEmpty)
            Text('${_currentIndex + 1}/${_items.length}', style: const TextStyle(fontFamily: 'Outfit', fontSize: 14, fontWeight: FontWeight.w600, color: AppTheme.darkTextSub)),
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_items.isEmpty) return const Center(child: Text('No ordering exercises available.', style: TextStyle(color: AppTheme.darkTextSub)));

    final item = _items[_currentIndex];
    final explanation = item['explanation'] as String? ?? '';

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Tap words to build the correct sentence:', style: TextStyle(fontFamily: 'Outfit', fontSize: 15, fontWeight: FontWeight.w600, color: AppTheme.darkTextSub)),
          const SizedBox(height: 16),

          // User sentence building area
          Container(
            constraints: const BoxConstraints(minHeight: 90),
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.darkCard,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: _isAnswered
                    ? (_isCorrect ? AppTheme.colorSuccess : AppTheme.colorError)
                    : AppTheme.darkCardBorder,
                width: _isAnswered ? 2 : 1,
              ),
            ),
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _userWords.map((word) => ActionChip(
                label: Text(word, style: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w600, color: AppTheme.darkText)),
                backgroundColor: _levelColor.withOpacity(0.2),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: BorderSide(color: _levelColor)),
                onPressed: () => _deselectWord(word),
              )).toList(),
            ),
          ).animate().fadeIn(duration: 300.ms),

          const SizedBox(height: 24),

          // Word Bank Chips
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: _bankWords.map((word) => ActionChip(
              label: Text(word, style: const TextStyle(fontFamily: 'Outfit', fontSize: 16, fontWeight: FontWeight.w500, color: AppTheme.darkText)),
              backgroundColor: AppTheme.darkCard,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: const BorderSide(color: AppTheme.darkCardBorder)),
              onPressed: () => _selectWord(word),
            )).toList(),
          ),

          const Spacer(),

          // Explanation card on wrong answer
          if (_isAnswered && explanation.isNotEmpty) ...[
            Directionality(
              textDirection: TextDirection.rtl,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: (_isCorrect ? AppTheme.colorSuccess : AppTheme.accentAmber).withOpacity(0.12),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: (_isCorrect ? AppTheme.colorSuccess : AppTheme.accentAmber).withOpacity(0.4)),
                ),
                child: Row(
                  children: [
                    Icon(_isCorrect ? Icons.check_circle_rounded : Icons.lightbulb_rounded, color: _isCorrect ? AppTheme.colorSuccess : AppTheme.accentAmber),
                    const SizedBox(width: 10),
                    Expanded(child: Text(explanation, textAlign: TextAlign.right, style: const TextStyle(fontFamily: 'Outfit', fontSize: 13, color: AppTheme.darkText, height: 1.5))),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // Check or Next CTA
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton.icon(
              onPressed: _isAnswered ? _onNext : _checkAnswer,
              icon: Icon(_isAnswered ? Icons.arrow_forward_rounded : Icons.check_circle_outline_rounded),
              label: Text(_isAnswered ? 'Next Question' : 'Check Order'),
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

