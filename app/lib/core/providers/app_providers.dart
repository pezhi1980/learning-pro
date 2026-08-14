// app/lib/core/providers/app_providers.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import '../services/client_cache_service.dart';

// ── Service Providers ───────────────────────────────────────────────────────

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

final cacheServiceProvider = Provider<ClientCacheService>((ref) {
  return ClientCacheService();
});

// ── Learner Auth State ─────────────────────────────────────────────────────

class AuthState {
  final String learnerId;
  final String displayName;
  final String level;
  final bool isAuthenticated;

  AuthState({
    this.learnerId = 'user_default_01',
    this.displayName = 'Learner',
    this.level = 'A1',
    this.isAuthenticated = true,
  });
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState());

  void setLearner(String id, String name, String level) {
    state = AuthState(learnerId: id, displayName: name, level: level, isAuthenticated: true);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});

// ── Daily Session State ────────────────────────────────────────────────────

class DailySessionState {
  final bool isLoading;
  final Map<String, dynamic>? sessionData;
  final String? error;

  DailySessionState({this.isLoading = false, this.sessionData, this.error});
}

class DailySessionNotifier extends StateNotifier<DailySessionState> {
  final ApiClient _apiClient;

  DailySessionNotifier(this._apiClient) : super(DailySessionState());

  Future<void> loadDailySession(String learnerId) async {
    state = DailySessionState(isLoading: true);
    try {
      final res = await _apiClient.post('/session/build', data: {'learner_id': learnerId});
      state = DailySessionState(isLoading: false, sessionData: res);
    } on AppException catch (e) {
      state = DailySessionState(isLoading: false, error: e.message);
    } catch (e) {
      state = DailySessionState(isLoading: false, error: 'Failed to build daily session.');
    }
  }
}

final sessionProvider = StateNotifierProvider<DailySessionNotifier, DailySessionState>((ref) {
  final client = ref.watch(apiClientProvider);
  return DailySessionNotifier(client);
});

// ── Bookmarks State ───────────────────────────────────────────────────────

class BookmarkNotifier extends StateNotifier<List<Map<String, dynamic>>> {
  final ApiClient _apiClient;

  BookmarkNotifier(this._apiClient) : super([]);

  Future<void> fetchBookmarks(String learnerId) async {
    try {
      final res = await _apiClient.get('/utilities/bookmarks/$learnerId');
      if (res is List) {
        state = res.cast<Map<String, dynamic>>();
      }
    } catch (_) {}
  }

  Future<void> addBookmark(String learnerId, String itemType, String itemId, String title) async {
    try {
      final res = await _apiClient.post(
        '/utilities/bookmarks/add',
        data: {'item_type': itemType, 'item_id': itemId, 'title': title},
      );
      if (res is Map<String, dynamic>) {
        state = [...state, res];
      }
    } catch (_) {}
  }
}

final bookmarkProvider = StateNotifierProvider<BookmarkNotifier, List<Map<String, dynamic>>>((ref) {
  final client = ref.watch(apiClientProvider);
  return BookmarkNotifier(client);
});

// ── Settings State ────────────────────────────────────────────────────────

class SettingsState {
  final int dailyGoalMinutes;
  final bool remindersEnabled;
  final String reminderTime;
  final bool audioAutoplay;
  final double playbackSpeed;
  final String uiTheme;
  final bool accessibilityHighContrast;
  final double fontScale;

  SettingsState({
    this.dailyGoalMinutes = 15,
    this.remindersEnabled = true,
    this.reminderTime = '20:00',
    this.audioAutoplay = true,
    this.playbackSpeed = 1.0,
    this.uiTheme = 'dark',
    this.accessibilityHighContrast = false,
    this.fontScale = 1.0,
  });

  factory SettingsState.fromJson(Map<String, dynamic> json) {
    return SettingsState(
      dailyGoalMinutes: json['daily_goal_minutes'] ?? 15,
      remindersEnabled: json['reminders_enabled'] ?? true,
      reminderTime: json['reminder_time'] ?? '20:00',
      audioAutoplay: json['audio_autoplay'] ?? true,
      playbackSpeed: (json['playback_speed'] as num?)?.toDouble() ?? 1.0,
      uiTheme: json['ui_theme'] ?? 'dark',
      accessibilityHighContrast: json['accessibility_high_contrast'] ?? false,
      fontScale: (json['font_scale'] as num?)?.toDouble() ?? 1.0,
    );
  }
}

class SettingsNotifier extends StateNotifier<SettingsState> {
  final ApiClient _apiClient;

  SettingsNotifier(this._apiClient) : super(SettingsState());

  Future<void> fetchSettings(String learnerId) async {
    try {
      final res = await _apiClient.get('/utilities/settings/$learnerId');
      if (res is Map<String, dynamic>) {
        state = SettingsState.fromJson(res);
      }
    } catch (_) {}
  }

  Future<void> updateSettings(String learnerId, Map<String, dynamic> updates) async {
    try {
      final res = await _apiClient.put('/utilities/settings/$learnerId', data: updates);
      if (res is Map<String, dynamic>) {
        state = SettingsState.fromJson(res);
      }
    } catch (_) {}
  }
}

final settingsProvider = StateNotifierProvider<SettingsNotifier, SettingsState>((ref) {
  final client = ref.watch(apiClientProvider);
  return SettingsNotifier(client);
});

// ── Search State ──────────────────────────────────────────────────────────

class SearchNotifier extends StateNotifier<List<Map<String, dynamic>>> {
  final ApiClient _apiClient;

  SearchNotifier(this._apiClient) : super([]);

  Future<void> query(String text, {String? level, String? targetType}) async {
    if (text.trim().isEmpty) {
      state = [];
      return;
    }
    try {
      final res = await _apiClient.get('/utilities/search', queryParameters: {
        'query': text,
        if (level != null) 'level': level,
        if (targetType != null) 'target_type': targetType,
      });
      if (res is List) {
        state = res.cast<Map<String, dynamic>>();
      }
    } catch (_) {
      state = [];
    }
  }
}

final searchProvider = StateNotifierProvider<SearchNotifier, List<Map<String, dynamic>>>((ref) {
  final client = ref.watch(apiClientProvider);
  return SearchNotifier(client);
});
