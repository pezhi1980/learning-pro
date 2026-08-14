// app/lib/core/utils/accessibility_helpers.dart

import 'package:flutter/material.dart';

/// Container enforcing minimum 48x48 dp touch target dimensions per WCAG & Material guidelines.
class AccessibleTouchTarget extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final String? label;
  final String? hint;

  const AccessibleTouchTarget({
    super.key,
    required this.child,
    this.onTap,
    this.label,
    this.hint,
  });

  @override
  Widget build(BuildContext context) {
    Widget content = ConstrainedBox(
      constraints: const BoxConstraints(
        minWidth: 48.0,
        minHeight: 48.0,
      ),
      child: Center(child: child),
    );

    if (onTap != null) {
      content = InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: content,
      );
    }

    if (label != null) {
      content = Semantics(
        label: label,
        hint: hint,
        button: onTap != null,
        enabled: onTap != null,
        child: content,
      );
    }

    return content;
  }
}

/// Breakpoint helper for Responsive Layouts (< 600 dp mobile vs >= 600 dp tablet/desktop).
class ResponsiveLayoutBuilder extends StatelessWidget {
  final Widget Function(BuildContext context, bool isTabletOrDesktop) builder;

  const ResponsiveLayoutBuilder({super.key, required this.builder});

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    final isTabletOrDesktop = width >= 600;
    return builder(context, isTabletOrDesktop);
  }
}

/// Checks if reduced motion animation is preferred by context media query.
bool shouldReduceMotion(BuildContext context) {
  return MediaQuery.of(context).disableAnimations;
}
