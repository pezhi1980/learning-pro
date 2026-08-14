// app/test/client_api_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_lang_pro/core/services/api_client.dart';

void main() {
  group('ApiClient Unit Tests', () {
    test('ApiClient initializes with default base URL and headers', () {
      final client = ApiClient(baseUrl: 'http://localhost:8000/api', learnerId: 'test_user_01');
      expect(client.learnerId, equals('test_user_01'));
      expect(client.adminKey, isNotEmpty);
    });

    test('AppException formats user-friendly error message without raw trace', () {
      final exc = AppException('Network timeout', statusCode: 429, isNetworkError: true);
      expect(exc.toString(), equals('Network timeout'));
      expect(exc.statusCode, equals(429));
      expect(exc.isNetworkError, isTrue);
    });
  });
}
