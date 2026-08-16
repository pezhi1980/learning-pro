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
        .select('*, languages!inner(code), levels!inner(code)')
        .eq('languages.code', languageId)
        .eq('levels.code', levelId)
        .eq('is_published', true)
        .order('order_index');
  }

  static Future<Map<String, dynamic>?> getGrammarContent({
    required String topicId,
    required String nativeLanguage,
  }) async {
    try {
      final result = await client
          .from('grammar_content')
          .select()
          .eq('topic_id', topicId)
          .eq('native_language', nativeLanguage)
          .maybeSingle();

      if (result != null) return result;

      // Fallback: If native language specific content is missing, fetch any existing content for topic
      final fallback = await client
          .from('grammar_content')
          .select()
          .eq('topic_id', topicId)
          .maybeSingle();

      return fallback;
    } catch (_) {
      return null;
    }
  }

  static Future<Map<String, dynamic>?> getGrammarContrast({
    required String topicId,
    required String targetLanguage,
    required String nativeLanguage,
  }) async {
    try {
      return await client
          .from('grammar_contrast')
          .select()
          .eq('topic_id', topicId)
          .eq('target_language', targetLanguage)
          .eq('native_language', nativeLanguage)
          .maybeSingle();
    } catch (_) {
      return null;
    }
  }

  // ── Session Caches & ID Resolvers ──────────────────────────────────
  static final Map<String, String> _languageIdCache = {};
  static final Map<String, String> _levelIdCache = {};

  static final RegExp _uuidRegex = RegExp(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$',
  );

  static Future<String> resolveLanguageId(String codeOrUuid) async {
    if (codeOrUuid.isEmpty) return codeOrUuid;
    if (_uuidRegex.hasMatch(codeOrUuid)) return codeOrUuid;
    if (_languageIdCache.containsKey(codeOrUuid)) {
      return _languageIdCache[codeOrUuid]!;
    }
    try {
      final res = await client
          .from('languages')
          .select('id')
          .eq('code', codeOrUuid)
          .maybeSingle();
      if (res != null && res['id'] != null) {
        final uuid = res['id'].toString();
        _languageIdCache[codeOrUuid] = uuid;
        return uuid;
      }
    } catch (_) {}
    return codeOrUuid;
  }

  static Future<String> resolveLevelId(String codeOrUuid) async {
    if (codeOrUuid.isEmpty) return codeOrUuid;
    if (_uuidRegex.hasMatch(codeOrUuid)) return codeOrUuid;
    if (_levelIdCache.containsKey(codeOrUuid)) {
      return _levelIdCache[codeOrUuid]!;
    }
    try {
      final res = await client
          .from('levels')
          .select('id')
          .eq('code', codeOrUuid)
          .maybeSingle();
      if (res != null && res['id'] != null) {
        final uuid = res['id'].toString();
        _levelIdCache[codeOrUuid] = uuid;
        return uuid;
      }
    } catch (_) {}
    return codeOrUuid;
  }

  // ── Vocabulary ─────────────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getVocabulary({
    required String languageId,
    required String levelId,
    int limit = 20,
    int offset = 0,
  }) async {
    final langUuid = await resolveLanguageId(languageId);
    final levelUuid = await resolveLevelId(levelId);

    try {
      final res = await client
          .from('vocabulary')
          .select('*, vocabulary_translations!inner(*)')
          .eq('language_id', langUuid)
          .eq('level_id', levelUuid)
          .eq('is_published', true)
          .range(offset, offset + limit - 1);
      return List<Map<String, dynamic>>.from(res);
    } catch (_) {
      try {
        final res = await client
            .from('vocabulary')
            .select('*, languages!inner(code), levels!inner(code), vocabulary_translations!inner(*)')
            .eq('languages.code', languageId)
            .eq('levels.code', levelId)
            .eq('is_published', true)
            .range(offset, offset + limit - 1);
        return List<Map<String, dynamic>>.from(res);
      } catch (e) {
        return [];
      }
    }
  }

  // ── Flashcards ─────────────────────────────────────────────
  static Future<List<Map<String, dynamic>>> getFlashcards({
    required String languageId,
    required String levelId,
    required String nativeLanguage,
  }) async {
    final langUuid = await resolveLanguageId(languageId);
    final levelUuid = await resolveLevelId(levelId);

    try {
      final res = await client
          .from('flashcards_with_vocab')
          .select()
          .eq('language_id', langUuid)
          .eq('level_id', levelUuid)
          .eq('native_language', nativeLanguage)
          .eq('is_approved', true);
      return List<Map<String, dynamic>>.from(res);
    } catch (_) {
      return [];
    }
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
    try {
      if (topicId != null && topicId.isNotEmpty) {
        final result = await client.rpc('get_random_exercises', params: {
          'p_topic_id': topicId,
          'p_limit': limit,
        });
        final list = List<Map<String, dynamic>>.from(result);
        if (list.isNotEmpty) return list;
      }

      final langUuid = await resolveLanguageId(languageId);
      final levelUuid = await resolveLevelId(levelId);

      final result = await client.rpc('get_random_exercises', params: {
        'p_language_id': langUuid,
        'p_level_id': levelUuid,
        'p_type': type,
        'p_limit': limit,
      });
      final list = List<Map<String, dynamic>>.from(result);
      if (list.isNotEmpty) return list;

      final fallback = await client.rpc('get_random_exercises', params: {
        'p_language_id': langUuid,
        'p_level_id': levelUuid,
        'p_type': type,
        'p_limit': limit,
      });
      return List<Map<String, dynamic>>.from(fallback);
    } catch (e) {
      return [];
    }
  }

  // ── User Progress ──────────────────────────────────────────
  static Future<void> updateProgress({
    required String languageId,
    required String levelId,
    String? topicId,
    required bool isCorrect,
  }) async {
    if (userId == null) return;
    final langUuid = await resolveLanguageId(languageId);
    final levelUuid = await resolveLevelId(levelId);

    try {
      await client.rpc('update_user_progress', params: {
        'p_user_id': userId,
        'p_language_id': langUuid,
        'p_level_id': levelUuid,
        'p_topic_id': topicId,
        'p_is_correct': isCorrect,
      });
    } catch (_) {}
  }

  static Future<List<Map<String, dynamic>>> getWeakTopics({
    required String languageId,
    required String levelId,
    int limit = 5,
  }) async {
    if (userId == null) return [];
    final langUuid = await resolveLanguageId(languageId);
    final levelUuid = await resolveLevelId(levelId);

    try {
      final res = await client.rpc('get_weak_topics', params: {
        'p_user_id': userId,
        'p_language_id': langUuid,
        'p_level_id': levelUuid,
        'p_limit': limit,
      });
      return List<Map<String, dynamic>>.from(res ?? []);
    } catch (_) {
      return [];
    }
  }
}

