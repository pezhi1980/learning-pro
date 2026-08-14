// app/lib/core/services/client_cache_service.dart

import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class CacheEntry {
  final dynamic data;
  final DateTime cachedAt;
  final Duration ttl;

  CacheEntry({
    required this.data,
    required this.cachedAt,
    this.ttl = const Duration(minutes: 10),
  });

  bool get isExpired => DateTime.now().difference(cachedAt) > ttl;

  Map<String, dynamic> toJson() => {
        'data': data,
        'cachedAt': cachedAt.toIso8601String(),
        'ttlMs': ttl.inMilliseconds,
      };

  factory CacheEntry.fromJson(Map<String, dynamic> json) {
    return CacheEntry(
      data: json['data'],
      cachedAt: DateTime.parse(json['cachedAt']),
      ttl: Duration(milliseconds: json['ttlMs'] ?? 600000),
    );
  }
}

/// Versioned content cache manager supporting TTL expiration and invalidation.
class ClientCacheService {
  final SharedPreferences? _prefs;
  final Map<String, CacheEntry> _memoryCache = {};

  ClientCacheService({SharedPreferences? prefs}) : _prefs = prefs;

  void setCache(String key, dynamic data, {Duration ttl = const Duration(minutes: 10)}) {
    final entry = CacheEntry(data: data, cachedAt: DateTime.now(), ttl: ttl);
    _memoryCache[key] = entry;

    if (_prefs != null) {
      try {
        _prefs!.setString('cache_$key', jsonEncode(entry.toJson()));
      } catch (_) {}
    }
  }

  dynamic getCache(String key) {
    // 1. Check memory cache
    final memEntry = _memoryCache[key];
    if (memEntry != null) {
      if (!memEntry.isExpired) {
        return memEntry.data;
      } else {
        _memoryCache.remove(key);
      }
    }

    // 2. Check disk cache
    if (_prefs != null) {
      final raw = _prefs!.getString('cache_$key');
      if (raw != null) {
        try {
          final json = jsonDecode(raw);
          final diskEntry = CacheEntry.fromJson(json);
          if (!diskEntry.isExpired) {
            _memoryCache[key] = diskEntry;
            return diskEntry.data;
          } else {
            _prefs!.remove('cache_$key');
          }
        } catch (_) {}
      }
    }

    return null;
  }

  void invalidateCache(String key) {
    _memoryCache.remove(key);
    if (_prefs != null) {
      _prefs!.remove('cache_$key');
    }
  }

  void clearAllCache() {
    _memoryCache.clear();
    if (_prefs != null) {
      final keys = _prefs!.getKeys().where((k) => k.startsWith('cache_')).toList();
      for (final k in keys) {
        _prefs!.remove(k);
      }
    }
  }
}
