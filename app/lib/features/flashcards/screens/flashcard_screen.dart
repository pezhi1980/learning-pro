import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class FlashcardScreen extends StatelessWidget {
  final String languageId; final String levelId;
  const FlashcardScreen({super.key, required this.languageId, required this.levelId,});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('FlashcardScreen')),
      body: const Center(child: Text('Coming soon...', style: TextStyle(color: AppTheme.darkTextSub))),
    );
  }
}
