import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class ExamScreen extends StatelessWidget {
  final String languageId; final String levelId;
  const ExamScreen({super.key, required this.languageId, required this.levelId,});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      appBar: AppBar(title: const Text('ExamScreen')),
      body: const Center(child: Text('Coming soon...', style: TextStyle(color: AppTheme.darkTextSub))),
    );
  }
}
