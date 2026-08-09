import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class LanguageSelectionScreen extends StatelessWidget {
  
  const LanguageSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('LanguageSelectionScreen')),
      body: const Center(child: Text('Coming soon...', style: TextStyle(color: AppTheme.darkTextSub))),
    );
  }
}
