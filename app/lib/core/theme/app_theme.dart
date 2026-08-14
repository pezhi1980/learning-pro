// lib/core/theme/app_theme.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  AppTheme._();

  // ── Color Palette ──────────────────────────────────────────
  static const Color primaryPurple   = Color(0xFF7C3AED); // Violet-600
  static const Color primaryColor    = primaryPurple;

  static const Color primaryTeal     = Color(0xFF0D9488); // Teal-600
  static const Color accentAmber     = Color(0xFFF59E0B); // Amber-500
  static const Color accentRose      = Color(0xFFF43F5E); // Rose-500
  static const Color accentEmerald   = Color(0xFF10B981); // Emerald-500

  // Dark theme colors
  static const Color darkBg          = Color(0xFF0A0A14); // near-black with purple tint
  static const Color darkSurface     = Color(0xFF12121F);
  static const Color darkCard        = Color(0xFF1A1A2E);
  static const Color darkCardBorder  = Color(0xFF2D2D4A);
  static const Color darkText        = Color(0xFFF1F0FF);
  static const Color darkTextSub     = Color(0xFF9896B8);
  static const Color darkDivider     = Color(0xFF2A2A40);

  // Light theme colors
  static const Color lightBg         = Color(0xFFF5F4FF);
  static const Color lightSurface    = Color(0xFFFFFFFF);
  static const Color lightCard       = Color(0xFFFFFFFF);
  static const Color lightCardBorder = Color(0xFFE5E4FF);
  static const Color lightText       = Color(0xFF1A1A2E);
  static const Color lightTextSub    = Color(0xFF6B6A8A);

  // Status colors
  static const Color colorSuccess    = Color(0xFF10B981);
  static const Color colorError      = Color(0xFFEF4444);
  static const Color colorWarning    = Color(0xFFF59E0B);
  static const Color colorInfo       = Color(0xFF3B82F6);

  // Gradient
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primaryPurple, primaryTeal],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient darkBgGradient = LinearGradient(
    colors: [Color(0xFF0A0A14), Color(0xFF0F0F22)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  // ── Typography ─────────────────────────────────────────────
  static TextTheme _buildTextTheme(Color textColor, bool isRtl) {
    final fontFamily = isRtl ? 'Vazirmatn' : GoogleFonts.outfit().fontFamily!;
    return TextTheme(
      // Display
      displayLarge: TextStyle(fontFamily: fontFamily, fontSize: 57, fontWeight: FontWeight.w700, color: textColor, letterSpacing: -0.25),
      displayMedium: TextStyle(fontFamily: fontFamily, fontSize: 45, fontWeight: FontWeight.w700, color: textColor),
      displaySmall: TextStyle(fontFamily: fontFamily, fontSize: 36, fontWeight: FontWeight.w600, color: textColor),
      // Headline
      headlineLarge: TextStyle(fontFamily: fontFamily, fontSize: 32, fontWeight: FontWeight.w700, color: textColor),
      headlineMedium: TextStyle(fontFamily: fontFamily, fontSize: 26, fontWeight: FontWeight.w600, color: textColor),
      headlineSmall: TextStyle(fontFamily: fontFamily, fontSize: 22, fontWeight: FontWeight.w600, color: textColor),
      // Title
      titleLarge: TextStyle(fontFamily: fontFamily, fontSize: 20, fontWeight: FontWeight.w600, color: textColor),
      titleMedium: TextStyle(fontFamily: fontFamily, fontSize: 16, fontWeight: FontWeight.w500, color: textColor),
      titleSmall: TextStyle(fontFamily: fontFamily, fontSize: 14, fontWeight: FontWeight.w500, color: textColor),
      // Body
      bodyLarge: TextStyle(fontFamily: fontFamily, fontSize: 16, fontWeight: FontWeight.w400, color: textColor, height: 1.6),
      bodyMedium: TextStyle(fontFamily: fontFamily, fontSize: 14, fontWeight: FontWeight.w400, color: textColor, height: 1.5),
      bodySmall: TextStyle(fontFamily: fontFamily, fontSize: 12, fontWeight: FontWeight.w400, color: textColor, height: 1.4),
      // Label
      labelLarge: TextStyle(fontFamily: fontFamily, fontSize: 14, fontWeight: FontWeight.w600, color: textColor),
      labelMedium: TextStyle(fontFamily: fontFamily, fontSize: 12, fontWeight: FontWeight.w500, color: textColor),
      labelSmall: TextStyle(fontFamily: fontFamily, fontSize: 11, fontWeight: FontWeight.w500, color: textColor),
    );
  }

  // ── Dark Theme ─────────────────────────────────────────────
  static ThemeData darkTheme({bool isRtl = false}) {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.dark(
        primary: primaryPurple,
        secondary: primaryTeal,
        tertiary: accentAmber,
        error: colorError,
        surface: darkSurface,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: darkText,
        outline: darkCardBorder,
      ),
      scaffoldBackgroundColor: darkBg,
      textTheme: _buildTextTheme(darkText, isRtl),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontFamily: isRtl ? 'Vazirmatn' : 'Outfit',
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: darkText,
        ),
        iconTheme: const IconThemeData(color: darkText),
      ),
      cardTheme: CardThemeData(
        color: darkCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: darkCardBorder, width: 1),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryPurple,
          foregroundColor: Colors.white,
          minimumSize: const Size(0, 56),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: TextStyle(
            fontFamily: isRtl ? 'Vazirmatn' : 'Outfit',
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
          elevation: 0,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryPurple,
          minimumSize: const Size(0, 56),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          side: const BorderSide(color: primaryPurple, width: 1.5),
          textStyle: TextStyle(
            fontFamily: isRtl ? 'Vazirmatn' : 'Outfit',
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: darkCard,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: darkCardBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: darkCardBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: primaryPurple, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: colorError),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        hintStyle: const TextStyle(color: darkTextSub),
      ),
      dividerTheme: const DividerThemeData(color: darkDivider, thickness: 1),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: darkCard,
        contentTextStyle: const TextStyle(color: darkText),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  // ── Light Theme ────────────────────────────────────────────
  static ThemeData lightTheme({bool isRtl = false}) {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.light(
        primary: primaryPurple,
        secondary: primaryTeal,
        tertiary: accentAmber,
        error: colorError,
        surface: lightSurface,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: lightText,
        outline: lightCardBorder,
      ),
      scaffoldBackgroundColor: lightBg,
      textTheme: _buildTextTheme(lightText, isRtl),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontFamily: isRtl ? 'Vazirmatn' : 'Outfit',
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: lightText,
        ),
        iconTheme: const IconThemeData(color: lightText),
      ),
      cardTheme: CardThemeData(
        color: lightCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: lightCardBorder, width: 1),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryPurple,
          foregroundColor: Colors.white,
          minimumSize: const Size(0, 56),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: TextStyle(
            fontFamily: isRtl ? 'Vazirmatn' : 'Outfit',
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
          elevation: 0,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: lightCard,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: lightCardBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: lightCardBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: primaryPurple, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        hintStyle: TextStyle(color: lightTextSub),
      ),
    );
  }
}
