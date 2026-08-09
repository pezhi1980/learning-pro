import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class LevelSelectionScreen extends StatelessWidget {
  final String languageId;
  const LevelSelectionScreen({super.key, required this.languageId,});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('LevelSelectionScreen')),
      body: const Center(child: Text('Coming soon...', style: TextStyle(color: AppTheme.darkTextSub))),
    );
  }
}
