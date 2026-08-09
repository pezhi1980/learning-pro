// lib/core/services/supabase_service.dart

import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseService {
  static SupabaseClient get client => Supabase.instance.client;
  static User? get currentUser => client.auth.currentUser;
  static bool get isLoggedIn => currentUser != null;
  static String? get userId => currentUser?.id;

  // ── Auth ───────────────────────────────────────────────────
  static Future<AuthResponse> signUp({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String nativeLanguage = 'fa',
  }) async {
    return await client.auth.signUp(
      email: email,
      password: password,
      data: {
        'first_name': firstName,
        'last_name': lastName,
        'native_language': nativeLanguage,
      },
    );
  }

  static Future<AuthResponse> signIn({
    required String email,
    required String password,
  }) async {
    return await client.auth.signInWithPassword(
      email: email,
      password: password,
    );
  }

  static Future<void> signOut() async {
    await client.auth.signOut();
  }

  static Future<void> resetPassword(String email) async {
    await client.auth.resetPasswordForEmail(email);
  }

  // ── Profile ────────────────────────────────────────────────
  static Future<Map<String, dynamic>?> getProfile() async {
    if (userId == null) return null;
    final response = await client
        .from('profiles')
        .select()
        .eq('id', userId!)
        .single();
    return response;
  }

  static Future<bool> isAdmin() async {
    final profile = await getProfile();
    return profile?['role'] == 'admin';
  }

  // ── Languages ──────────────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getActiveLanguages() async {
    return await client
        .from('languages')
        .select()
        .eq('is_active', true)
        .order('order_index');
  }

  // ── Levels ─────────────────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getLevels() async {
    return await client
        .from('levels')
        .select()
        .order('order_index');
  }

  // ── Grammar Topics ─────────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getGrammarTopics({
    required String languageId,
    required String levelId,
  }) async {
    return await client
        .from('grammar_topics')
        .select()
        .eq('language_id', languageId)
        .eq('level_id', levelId)
        .eq('is_published', true)
        .order('order_index');
  }

  static Future<Map<String, dynamic>?> getGrammarContent({
    required String topicId,
    required String nativeLanguage,
  }) async {
    final result = await client
        .from('grammar_content')
        .select()
        .eq('topic_id', topicId)
        .eq('native_language', nativeLanguage)
        .maybeSingle();
    return result;
  }

  static Future<Map<String, dynamic>?> getGrammarContrast({
    required String topicId,
    required String targetLanguage,
    required String nativeLanguage,
  }) async {
    return await client
        .from('grammar_contrast')
        .select()
        .eq('topic_id', topicId)
        .eq('target_language', targetLanguage)
        .eq('native_language', nativeLanguage)
        .maybeSingle();
  }

  // ── Vocabulary ─────────────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getVocabulary({
    required String languageId,
    required String levelId,
    int limit = 20,
    int offset = 0,
  }) async {
    return await client
        .from('vocabulary')
        .select('*, vocabulary_translations!inner(*)')
        .eq('language_id', languageId)
        .eq('level_id', levelId)
        .eq('is_published', true)
        .range(offset, offset + limit - 1);
  }

  // ── Flashcards ─────────────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getFlashcards({
    required String languageId,
    required String levelId,
    required String nativeLanguage,
  }) async {
    return await client
        .from('flashcards_with_vocab')
        .select()
        .eq('language_id', languageId)
        .eq('level_id', levelId)
        .eq('native_language', nativeLanguage)
        .eq('is_approved', true);
  }

  // ── Exercises ──────────────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getExercises({
    required String languageId,
    required String levelId,
    required String type,
    required String nativeLanguage,
    String? topicId,
    int limit = 5,
  }) async {
    var query = client
        .from('exercises')
        .select()
        .eq('language_id', languageId)
        .eq('level_id', levelId)
        .eq('type', type)
        .eq('native_language', nativeLanguage)
        .eq('is_approved', true);

    if (topicId != null) {
      query = query.eq('topic_id', topicId);
    }

    // Random selection using order by random
    return await query.limit(limit);
  }

  // ── User Progress ──────────────────────────────────────────
  static Future<void> updateProgress({
    required String languageId,
    required String levelId,
    String? topicId,
    required bool isCorrect,
  }) async {
    if (userId == null) return;

    await client.rpc('update_user_progress', params: {
      'p_user_id': userId,
      'p_language_id': languageId,
      'p_level_id': levelId,
      'p_topic_id': topicId,
      'p_is_correct': isCorrect,
    });
  }

  static Future<List<Map<String, dynamic>>> getWeakTopics({
    required String languageId,
    required String levelId,
    int limit = 5,
  }) async {
    if (userId == null) return [];
    return await client.rpc('get_weak_topics', params: {
      'p_user_id': userId,
      'p_language_id': languageId,
      'p_level_id': levelId,
      'p_limit': limit,
    });
  }
}
