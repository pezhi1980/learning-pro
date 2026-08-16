// lib/features/home/language_selection_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/router.dart';
import '../../core/services/supabase_service.dart';

class LanguageSelectionScreen extends StatefulWidget {
  const LanguageSelectionScreen({super.key});

  @override
  State<LanguageSelectionScreen> createState() => _LanguageSelectionScreenState();
}

class _LanguageSelectionScreenState extends State<LanguageSelectionScreen> {
  String? _selectedLanguageId;

  // Static language data — will come from Supabase once more are added
  final List<_LanguageItem> _languages = const [
    _LanguageItem(
      id: 'en',
      name: 'English',
      nativeName: 'English',
      flag: '🇬🇧',
      isActive: true,
      description: 'A1 → C2 · Full content available',
    ),
    _LanguageItem(
      id: 'fr',
      name: 'French',
      nativeName: 'Français',
      flag: '🇫🇷',
      isActive: false,
      description: 'Coming soon',
    ),
    _LanguageItem(
      id: 'de',
      name: 'German',
      nativeName: 'Deutsch',
      flag: '🇩🇪',
      isActive: false,
      description: 'Coming soon',
    ),
    _LanguageItem(
      id: 'it',
      name: 'Italian',
      nativeName: 'Italiano',
      flag: '🇮🇹',
      isActive: false,
      description: 'Coming soon',
    ),
    _LanguageItem(
      id: 'es',
      name: 'Spanish',
      nativeName: 'Español',
      flag: '🇪🇸',
      isActive: false,
      description: 'Coming soon',
    ),
  ];

  String _getUserFirstName() {
    final user = Supabase.instance.client.auth.currentUser;
    final firstName = user?.userMetadata?['first_name'] as String?;
    return firstName ?? 'there';
  }

  void _onLanguageSelected(String id, bool isActive) {
    if (!isActive) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('This language is coming soon! Stay tuned.'),
          backgroundColor: AppTheme.darkCard,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      );
      return;
    }
    setState(() => _selectedLanguageId = id);
  }

  void _onContinue() {
    if (_selectedLanguageId == null) return;
    context.push('/category-select/$_selectedLanguageId');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.darkBgGradient),
        child: Stack(
          children: [
            // Background decorative blobs
            Positioned(
              top: -100,
              right: -80,
              child: Container(
                width: 280,
                height: 280,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(colors: [
                    AppTheme.primaryPurple.withOpacity(0.2),
                    Colors.transparent,
                  ]),
                ),
              ),
            ),
            Positioned(
              bottom: 150,
              left: -80,
              child: Container(
                width: 220,
                height: 220,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(colors: [
                    AppTheme.primaryTeal.withOpacity(0.15),
                    Colors.transparent,
                  ]),
                ),
              ),
            ),

            SafeArea(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  _buildHeader(),

                  const SizedBox(height: 8),

                  // Subtitle
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    child: Text(
                      'What language do you want to learn?',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: AppTheme.darkTextSub,
                          ),
                    ).animate().fadeIn(delay: 200.ms),
                  ),

                  const SizedBox(height: 32),

                  // Language cards
                  Expanded(
                    child: ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      itemCount: _languages.length,
                      itemBuilder: (context, index) {
                        final lang = _languages[index];
                        final isSelected = _selectedLanguageId == lang.id;
                        return _LanguageCard(
                          language: lang,
                          isSelected: isSelected,
                          onTap: () => _onLanguageSelected(lang.id, lang.isActive),
                          animDelay: (index * 80).ms,
                        );
                      },
                    ),
                  ),

                  // Continue button
                  _buildContinueButton(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top row: logo + sign out
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  gradient: AppTheme.primaryGradient,
                ),
                child: const Icon(Icons.translate_rounded, size: 22, color: Colors.white),
              ),
              IconButton(
                icon: const Icon(Icons.logout_rounded, color: AppTheme.darkTextSub),
                onPressed: () async {
                  await SupabaseService.signOut();
                  if (mounted) context.go(AppRoutes.login);
                },
              ),
            ],
          ).animate().fadeIn(duration: 400.ms),

          const SizedBox(height: 20),

          Text(
            'Hello, ${_getUserFirstName()}! 👋',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: AppTheme.darkTextSub,
                  fontWeight: FontWeight.w400,
                ),
          ).animate().fadeIn(delay: 100.ms),

          const SizedBox(height: 4),

          Text(
            'Choose a Language',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  color: AppTheme.darkText,
                  fontWeight: FontWeight.w700,
                ),
          ).animate().fadeIn(delay: 150.ms).slideY(begin: 0.3, end: 0),
        ],
      ),
    );
  }

  Widget _buildContinueButton() {
    final isEnabled = _selectedLanguageId != null;
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 300),
        opacity: isEnabled ? 1.0 : 0.4,
        child: SizedBox(
          width: double.infinity,
          height: 56,
          child: DecoratedBox(
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(14),
              boxShadow: isEnabled
                  ? [
                      BoxShadow(
                        color: AppTheme.primaryPurple.withOpacity(0.4),
                        blurRadius: 20,
                        offset: const Offset(0, 6),
                      ),
                    ]
                  : null,
            ),
            child: ElevatedButton(
              onPressed: isEnabled ? _onContinue : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  Text(
                    'Continue',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                  SizedBox(width: 8),
                  Icon(Icons.arrow_forward_rounded, color: Colors.white, size: 20),
                ],
              ),
            ),
          ),
        ),
      ),
    ).animate().fadeIn(delay: 500.ms).slideY(begin: 0.3, end: 0);
  }
}

// ── Language Card ───────────────────────────────────────────

class _LanguageCard extends StatelessWidget {
  final _LanguageItem language;
  final bool isSelected;
  final VoidCallback onTap;
  final Duration animDelay;

  const _LanguageCard({
    required this.language,
    required this.isSelected,
    required this.onTap,
    required this.animDelay,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.primaryPurple.withOpacity(0.15) : AppTheme.darkCard,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: isSelected
                  ? AppTheme.primaryPurple
                  : language.isActive
                      ? AppTheme.darkCardBorder
                      : AppTheme.darkCardBorder.withOpacity(0.5),
              width: isSelected ? 2 : 1,
            ),
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: AppTheme.primaryPurple.withOpacity(0.2),
                      blurRadius: 16,
                      spreadRadius: 1,
                    ),
                  ]
                : null,
          ),
          child: Row(
            children: [
              // Flag
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: language.isActive
                      ? AppTheme.darkSurface
                      : AppTheme.darkSurface.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Center(
                  child: Text(
                    language.flag,
                    style: TextStyle(
                      fontSize: 26,
                      color: language.isActive ? null : const Color(0xFF555566),
                    ),
                  ),
                ),
              ),

              const SizedBox(width: 16),

              // Name + description
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          language.name,
                          style: TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 17,
                            fontWeight: FontWeight.w600,
                            color: language.isActive ? AppTheme.darkText : AppTheme.darkTextSub,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          language.nativeName,
                          style: const TextStyle(
                            fontFamily: 'Outfit',
                            fontSize: 13,
                            color: AppTheme.darkTextSub,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      language.description,
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontSize: 12,
                        color: language.isActive
                            ? AppTheme.primaryTeal
                            : AppTheme.darkTextSub.withOpacity(0.5),
                      ),
                    ),
                  ],
                ),
              ),

              // Selected indicator or lock
              if (language.isActive)
                AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isSelected ? AppTheme.primaryPurple : Colors.transparent,
                    border: Border.all(
                      color: isSelected ? AppTheme.primaryPurple : AppTheme.darkCardBorder,
                      width: 2,
                    ),
                  ),
                  child: isSelected
                      ? const Icon(Icons.check_rounded, size: 14, color: Colors.white)
                      : null,
                )
              else
                Icon(
                  Icons.lock_outline_rounded,
                  size: 18,
                  color: AppTheme.darkTextSub.withOpacity(0.4),
                ),
            ],
          ),
        ),
      ),
    )
        .animate()
        .fadeIn(delay: animDelay, duration: 400.ms)
        .slideX(begin: 0.15, end: 0, delay: animDelay, duration: 400.ms);
  }
}

// ── Data model ─────────────────────────────────────────────

class _LanguageItem {
  final String id;
  final String name;
  final String nativeName;
  final String flag;
  final bool isActive;
  final String description;

  const _LanguageItem({
    required this.id,
    required this.name,
    required this.nativeName,
    required this.flag,
    required this.isActive,
    required this.description,
  });
}
