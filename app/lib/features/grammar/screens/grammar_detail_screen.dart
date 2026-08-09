import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class GrammarDetailScreen extends StatelessWidget {
  final String languageId; final String levelId; final String topicId;
  const GrammarDetailScreen({super.key, required this.languageId, required this.levelId, this.topicId,});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('GrammarDetailScreen')),
      body: const Center(child: Text('Coming soon...', style: TextStyle(color: AppTheme.darkTextSub))),
    );
  }
}
