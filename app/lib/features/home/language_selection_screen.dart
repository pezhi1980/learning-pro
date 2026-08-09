import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/utils/router.dart';

class LanguageSelectionScreen extends StatefulWidget {
  const LanguageSelectionScreen({super.key});

  @override
  State<LanguageSelectionScreen> createState() => _LanguageSelectionScreenState();
}

class _LanguageSelectionScreenState extends State<LanguageSelectionScreen> {
  // Mock data - In the future, this will come from SupabaseService.getActiveLanguages()
  final List<Map<String, dynamic>> _languages = [
    {
      'id': 'en',
      'name': 'English',
      'native_name': 'English',
      'flag': '🇬🇧',
      'color': const Color(0xFF3B82F6), // Blue
      'description': 'The global language of business and travel.',
    },
    {
      'id': 'fr',
      'name': 'French',
      'native_name': 'Français',
      'flag': '🇫🇷',
      'color': const Color(0xFF8B5CF6), // Purple
      'description': 'The language of love, culture, and diplomacy.',
    },
    {
      'id': 'de',
      'name': 'German',
      'native_name': 'Deutsch',
      'flag': '🇩🇪',
      'color': const Color(0xFFF59E0B), // Amber
      'description': 'The language of science, philosophy, and engineering.',
    },
    {
      'id': 'it',
      'name': 'Italian',
      'native_name': 'Italiano',
      'flag': '🇮🇹',
      'color': const Color(0xFF10B981), // Emerald
      'description': 'The language of art, music, and culinary delights.',
    },
    {
      'id': 'es',
      'name': 'Spanish',
      'native_name': 'Español',
      'flag': '🇪🇸',
      'color': const Color(0xFFEF4444), // Red
      'description': 'The second most spoken native language globally.',
    },
  ];

  String? _selectedLanguageId;

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
              const SizedBox(height: 24),
              _buildHeader(),
              const SizedBox(height: 32),
              Expanded(child: _buildLanguageGrid()),
              _buildBottomButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.darkCard,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.darkCardBorder),
                ),
                child: const Icon(Icons.language_rounded, color: Colors.white, size: 24),
              ).animate().scale(duration: 400.ms, curve: Curves.easeOutBack),
              
              // Profile or Settings Button
              IconButton(
                onPressed: () {},
                icon: const Icon(Icons.settings_rounded, color: AppTheme.darkTextSub),
              ).animate().fadeIn(delay: 200.ms),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'What would you like\nto learn today?',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  color: AppTheme.darkText,
                  fontWeight: FontWeight.w700,
                  height: 1.2,
                ),
          ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2, end: 0),
          const SizedBox(height: 12),
          Text(
            'Select a target language to continue',
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: AppTheme.darkTextSub,
                ),
          ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.2, end: 0),
        ],
      ),
    );
  }

  Widget _buildLanguageGrid() {
    return GridView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
      physics: const BouncingScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.85,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: _languages.length,
      itemBuilder: (context, index) {
        final lang = _languages[index];
        final isSelected = _selectedLanguageId == lang['id'];
        
        return GestureDetector(
          onTap: () {
            setState(() {
              _selectedLanguageId = lang['id'];
            });
          },
          child: AnimatedContainer(
            duration: AppTheme.animNormal,
            curve: Curves.easeOutCubic,
            decoration: BoxDecoration(
              color: isSelected ? lang['color'].withOpacity(0.15) : AppTheme.darkCard,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(
                color: isSelected ? lang['color'] : AppTheme.darkCardBorder,
                width: isSelected ? 2 : 1,
              ),
              boxShadow: isSelected
                  ? [
                      BoxShadow(
                        color: lang['color'].withOpacity(0.2),
                        blurRadius: 20,
                        spreadRadius: 2,
                      )
                    ]
                  : [],
            ),
            child: Stack(
              children: [
                if (isSelected)
                  Positioned(
                    top: 12,
                    right: 12,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: lang['color'],
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.check_rounded, color: Colors.white, size: 16),
                    ).animate().scale(duration: 300.ms, curve: Curves.easeOutBack),
                  ),
                Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        lang['flag'],
                        style: const TextStyle(fontSize: 42),
                      ).animate(target: isSelected ? 1 : 0)
                          .scale(begin: const Offset(1, 1), end: const Offset(1.1, 1.1)),
                      const Spacer(),
                      Text(
                        lang['native_name'],
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: isSelected ? lang['color'] : AppTheme.darkText,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        lang['name'],
                        style: TextStyle(
                          fontFamily: 'Outfit',
                          fontSize: 14,
                          color: AppTheme.darkTextSub,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ).animate().fadeIn(delay: Duration(milliseconds: 100 * index)).slideY(begin: 0.1, end: 0);
      },
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
            onPressed: _selectedLanguageId == null
                ? null
                : () {
                    context.push(AppRoutes.levelSelect.replaceFirst(':languageId', _selectedLanguageId!));
                  },
            style: ElevatedButton.styleFrom(
              backgroundColor: _selectedLanguageId != null ? AppTheme.primaryPurple : AppTheme.darkCard,
              foregroundColor: _selectedLanguageId != null ? Colors.white : AppTheme.darkTextSub,
              disabledBackgroundColor: AppTheme.darkCard,
              disabledForegroundColor: AppTheme.darkTextSub,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              elevation: _selectedLanguageId != null ? 8 : 0,
              shadowColor: AppTheme.primaryPurple.withOpacity(0.5),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Continue',
                  style: const TextStyle(
                    fontFamily: 'Outfit',
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(width: 8),
                const Icon(Icons.arrow_forward_rounded, size: 20),
              ],
            ),
          ),
        ),
      ),
    ).animate().slideY(begin: 1, end: 0, duration: 500.ms, curve: Curves.easeOutCubic);
  }
}
