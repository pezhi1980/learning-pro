// lib/shared/widgets/loading_shimmer.dart

import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';
import '../../core/theme/app_theme.dart';

class LoadingShimmerCard extends StatelessWidget {
  final double height;
  final double borderRadius;

  const LoadingShimmerCard({
    super.key,
    this.height = 80,
    this.borderRadius = 16,
  });

  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: AppTheme.darkCard,
      highlightColor: AppTheme.darkCardBorder,
      child: Container(
        height: height,
        margin: const EdgeInsets.only(bottom: 12),
        decoration: BoxDecoration(
          color: AppTheme.darkCard,
          borderRadius: BorderRadius.circular(borderRadius),
        ),
      ),
    );
  }
}

class LoadingShimmerList extends StatelessWidget {
  final int count;
  final double cardHeight;

  const LoadingShimmerList({super.key, this.count = 5, this.cardHeight = 80});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(
        count,
        (i) => LoadingShimmerCard(height: cardHeight),
      ),
    );
  }
}
