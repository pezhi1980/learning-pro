// lib/features/vocabulary/screens/vocabulary_list_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:go_router/go_router.dart';

import '../../../core/services/supabase_service.dart';
import '../../../core/theme/app_theme.dart';
import '../../../shared/widgets/loading_shimmer.dart';

class VocabularyListScreen extends StatefulWidget {
  final String languageId;
  final String levelId;

  const VocabularyListScreen({
    super.key,
    required this.languageId,
    required this.levelId,
  });

  @override
  State<VocabularyListScreen> createState() => _VocabularyListScreenState();
}

class _VocabularyListScreenState extends State<VocabularyListScreen> {
  late String _currentLevel;
  List<Map<String, dynamic>> _vocabularyList = [];
  List<Map<String, dynamic>> _filteredList = [];
  bool _isLoading = true;
  String? _error;
  String _searchQuery = '';
  final TextEditingController _searchController = TextEditingController();
  final FlutterTts _flutterTts = FlutterTts();

  static const List<String> _levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

  static const Map<String, Color> _levelColors = {
    'A1': Color(0xFF10B981),
    'A2': Color(0xFF06B6D4),
    'B1': Color(0xFF3B82F6),
    'B2': Color(0xFF8B5CF6),
    'C1': Color(0xFFEC4899),
    'C2': Color(0xFFF59E0B),
  };

  Color get _levelColor => _levelColors[_currentLevel] ?? AppTheme.primaryPurple;

  String get _languageFlag {
    const flags = {'en': '🇬🇧', 'fr': '🇫🇷', 'de': '🇩🇪', 'it': '🇮🇹', 'es': '🇪🇸'};
    return flags[widget.languageId] ?? '🌐';
  }

  @override
  void initState() {
    super.initState();
    _currentLevel = widget.levelId;
    _initTts();
    _loadVocabulary();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _flutterTts.stop();
    super.dispose();
  }

  Future<void> _initTts() async {
    try {
      await _flutterTts.setLanguage(widget.languageId == 'en' ? 'en-US' : widget.languageId);
      await _flutterTts.setSpeechRate(0.45);
    } catch (_) {}
  }

  void _speak(String text) async {
    try {
      await _flutterTts.speak(text);
    } catch (_) {}
  }

  Future<void> _loadVocabulary() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final data = await SupabaseService.getVocabulary(
        languageId: widget.languageId,
        levelId: _currentLevel,
        limit: 100,
      );

      if (mounted) {
        setState(() {
          _vocabularyList = data;
          _applySearch();
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

  void _applySearch() {
    if (_searchQuery.trim().isEmpty) {
      _filteredList = List.from(_vocabularyList);
    } else {
      final q = _searchQuery.toLowerCase().trim();
      _filteredList = _vocabularyList.where((item) {
        final lexeme = (item['lexeme'] ?? '').toString().toLowerCase();
        final guideword = (item['guideword'] ?? '').toString().toLowerCase();
        final pos = (item['pos'] ?? '').toString().toLowerCase();
        return lexeme.contains(q) || guideword.contains(q) || pos.contains(q);
      }).toList();
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
              _buildLevelSelector(),
              _buildSearchBar(),
              Expanded(child: _buildBody()),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 20, 8),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded, color: AppTheme.darkText, size: 20),
            onPressed: () {
              if (context.canPop()) {
                context.pop();
              } else {
                context.go('/category-select/${widget.languageId}');
              }
            },
          ),
          const SizedBox(width: 4),
          Text(
            'Vocabulary',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontFamily: 'Outfit',
                  color: AppTheme.darkText,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: AppTheme.darkCard,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.darkCardBorder),
            ),
            child: Row(
              children: [
                Text(_languageFlag, style: const TextStyle(fontSize: 16)),
                const SizedBox(width: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: _levelColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    _currentLevel,
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: _levelColor,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLevelSelector() {
    return SizedBox(
      height: 44,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        scrollDirection: Axis.horizontal,
        itemCount: _levels.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, i) {
          final lvl = _levels[i];
          final isSelected = lvl == _currentLevel;
          final color = _levelColors[lvl] ?? AppTheme.primaryPurple;

          return GestureDetector(
            onTap: () {
              if (_currentLevel != lvl) {
                setState(() => _currentLevel = lvl);
                _loadVocabulary();
              }
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: isSelected ? color.withOpacity(0.2) : AppTheme.darkCard,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isSelected ? color : AppTheme.darkCardBorder,
                  width: isSelected ? 1.5 : 1,
                ),
              ),
              child: Center(
                child: Text(
                  lvl,
                  style: TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 13,
                    fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                    color: isSelected ? color : AppTheme.darkTextSub,
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 12),
      child: TextField(
        controller: _searchController,
        style: const TextStyle(color: AppTheme.darkText, fontSize: 14),
        onChanged: (val) {
          setState(() {
            _searchQuery = val;
            _applySearch();
          });
        },
        decoration: InputDecoration(
          hintText: 'Search words, meanings...',
          hintStyle: const TextStyle(color: AppTheme.darkTextSub, fontSize: 14),
          prefixIcon: const Icon(Icons.search_rounded, color: AppTheme.darkTextSub, size: 20),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear_rounded, color: AppTheme.darkTextSub, size: 18),
                  onPressed: () {
                    _searchController.clear();
                    setState(() {
                      _searchQuery = '';
                      _applySearch();
                    });
                  },
                )
              : null,
          filled: true,
          fillColor: AppTheme.darkCard,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: AppTheme.darkCardBorder),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: AppTheme.darkCardBorder),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide(color: _levelColor, width: 1.5),
          ),
        ),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        itemCount: 6,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (_, __) => const LoadingShimmerCard(height: 90, borderRadius: 16),
      );
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline_rounded, color: AppTheme.accentAmber, size: 48),
              const SizedBox(height: 16),
              Text(
                'Could not load vocabulary',
                style: const TextStyle(color: AppTheme.darkText, fontSize: 16, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Text(
                _error!,
                style: const TextStyle(color: AppTheme.darkTextSub, fontSize: 12),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: _loadVocabulary,
                icon: const Icon(Icons.refresh_rounded, size: 18),
                label: const Text('Try Again'),
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

    if (_filteredList.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.style_outlined, color: AppTheme.darkTextSub.withOpacity(0.5), size: 56),
            const SizedBox(height: 16),
            Text(
              _searchQuery.isNotEmpty ? 'No words match "$_searchQuery"' : 'No vocabulary found for $_currentLevel',
              style: const TextStyle(color: AppTheme.darkTextSub, fontSize: 15),
            ),
          ],
        ),
      );
    }

    return ListView.separated(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      itemCount: _filteredList.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final item = _filteredList[index];
        final lexeme = item['lexeme'] ?? '';
        final pos = item['pos'] ?? '';
        final guideword = item['guideword'] ?? '';
        final translations = item['vocabulary_translations'] as List<dynamic>?;
        final firstTrans = (translations != null && translations.isNotEmpty) ? translations.first : null;
        final translationText = firstTrans != null ? (firstTrans['translation'] ?? '') : '';

        return _VocabularyCard(
          lexeme: lexeme,
          pos: pos,
          guideword: guideword,
          translation: translationText,
          levelColor: _levelColor,
          onSpeak: () => _speak(lexeme),
          animDelay: (index * 40).ms,
        );
      },
    );
  }
}

class _VocabularyCard extends StatelessWidget {
  final String lexeme;
  final String pos;
  final String guideword;
  final String translation;
  final Color levelColor;
  final VoidCallback onSpeak;
  final Duration animDelay;

  const _VocabularyCard({
    required this.lexeme,
    required this.pos,
    required this.guideword,
    required this.translation,
    required this.levelColor,
    required this.onSpeak,
    required this.animDelay,
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
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Audio speaker button
          IconButton(
            icon: const Icon(Icons.volume_up_rounded, color: AppTheme.primaryTeal, size: 22),
            onPressed: onSpeak,
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
          const SizedBox(width: 14),

          // Lexeme and details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      lexeme,
                      style: const TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 17,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.darkText,
                      ),
                    ),
                    if (pos.isNotEmpty) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.darkSurface,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          pos,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 11,
                            color: AppTheme.darkTextSub,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                if (guideword.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    '($guideword)',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 12,
                      color: levelColor.withOpacity(0.9),
                    ),
                  ),
                ],
                if (translation.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Text(
                    translation,
                    style: const TextStyle(
                      fontSize: 14,
                      color: AppTheme.darkTextSub,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: animDelay, duration: 300.ms).slideY(begin: 0.1, end: 0);
  }
}
